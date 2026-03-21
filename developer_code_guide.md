# Guia do Desenvolvedor - Explicação Detalhada do Código

Este documento complementa a documentação técnica, fornecendo uma explicação detalhada de cada arquivo Python, suas classes, funções e funcionalidades. O foco é ajudar desenvolvedores a entenderem como o código funciona internamente e como os componentes interagem no pipeline ETL.

## 1. Script de Entrada: `run_scraper.py`

**Localização:** Raiz do projeto (`/run_scraper.py`)

**Propósito:** Ponto de entrada principal para execução local do scraper IBOV.

### Estrutura do Código

```python
#!/usr/bin/env python3
"""
Script principal para executar o scraper do IBOV.
"""

import sys
import os

# Adiciona o diretório raiz ao path para permitir imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scraper_ibov_day import main

if __name__ == "__main__":
    main()
```

### Funcionalidades

- **Configuração do Path:** Adiciona o diretório raiz ao `sys.path` para permitir imports relativos dos módulos em `app/`
- **Execução:** Importa e chama a função `main()` do módulo `scraper_ibov_day`
- **Código de Saída:** Retorna 0 em sucesso, 1 em falha (baseado no retorno de `main()`)

### Fluxo de Execução

1. Configura ambiente Python
2. Importa função `main` do scraper
3. Executa o scraping
4. Encerra com código apropriado

---

## 2. Scraper Local: `app/services/scraper_ibov_day.py`

**Propósito:** Implementa a classe `IBOVScraper` para coleta local de dados do IBOV.

### Classe `IBOVScraper`

#### Atributos de Instância

- `base_url`: URL da API da B3 para dados do portfólio diário
- `execution_time`: Data atual no formato YYYY-MM-DD
- `partition_column`: Nome da coluna de partição ("anomesdia")
- `output_folder`: Pasta local para saída ("data_exec")
- `output_file`: Caminho do arquivo de saída (inicialmente None)

#### Métodos Principais

##### `__init__()`
Inicializa todos os atributos da instância.

##### `_encode_params(page: int) -> str`
- **Parâmetro:** Número da página a ser requisitada
- **Retorno:** String codificada em base64 com os parâmetros da requisição
- **Funcionalidade:** Prepara payload JSON e codifica para envio na URL

##### `_get_page(page: int) -> dict`
- **Parâmetro:** Número da página
- **Retorno:** Dicionário JSON da resposta ou None em erro
- **Funcionalidade:**
  - Monta URL completa com parâmetros codificados
  - Faz requisição HTTP GET com timeout de 30s
  - Trata erros de rede e HTTP

##### `_extract_table_data(json_data: dict) -> List[Dict]`
- **Parâmetro:** Resposta JSON da API
- **Retorno:** Lista de dicionários com dados extraídos
- **Funcionalidade:**
  - Extrai array "results" do JSON
  - Para cada item, limpa e estrutura os dados usando funções utilitárias
  - Campos extraídos: codigo, acao, tipo, qtde_teorica, part_pct, anomesdia

##### `_scrape() -> List[Dict]`
- **Retorno:** Lista completa de todos os dados coletados
- **Funcionalidade:**
  - Itera sobre páginas (1, 2, 3, ...)
  - Coleta dados de cada página até não haver mais resultados
  - Acumula todos os registros em uma lista

##### `_validate_data(data: List[Dict]) -> List[Dict]`
- **Parâmetro:** Lista de dados brutos
- **Retorno:** Lista de dados validados (sem duplicatas)
- **Funcionalidade:**
  - Remove registros duplicados baseados no campo "codigo"
  - Mantém apenas a primeira ocorrência de cada código

##### `_save_parquet(data: List[Dict], local: bool = True) -> bool`
- **Parâmetros:** Dados a salvar, flag para salvar localmente
- **Retorno:** True se sucesso, False se erro
- **Funcionalidade:**
  - Salva dados em formato JSON localmente (não Parquet como o nome sugere)
  - Caminho: "dados2.json"
  - Trata exceções de I/O

##### `run() -> bool`
- **Retorno:** True se execução completa com sucesso
- **Funcionalidade:**
  - Coordena todo o processo de scraping
  - Chama métodos em sequência: _scrape → _validate_data → _save_parquet
  - Exibe resumo final com contagem de registros
  - Retorna status de sucesso

### Função `main()`

- Instancia `IBOVScraper`
- Chama método `run()`
- Define código de saída baseado no resultado

---

## 3. Glue Job de Extração: `app/services/glue_extract_data.py`

**Propósito:** Versão do scraper otimizada para execução em AWS Glue.

### Diferenças do Scraper Local

- Salva dados diretamente no S3 em formato Parquet
- Usa particionamento por data
- Inclui constantes S3 no código

### Classe `IBOVScraper` (Similar ao arquivo anterior)

Mesmos métodos e atributos, com diferenças em `_save_parquet`:

- **Parâmetro `local`:** Sempre False (salva no S3)
- **Formato:** Parquet com particionamento
- **Destino:** `s3://mlet8-fase2-pos/mlte8-scraping/`
- **Engine:** PyArrow

### Funções Utilitárias (Duplicadas)

- `clean_number(value: str) -> int`
- `clean_percentage(value: str) -> float`  
- `clean_text(value: str) -> str`

Essas funções são cópias das que estão em `app/utils/data_cleaners.py`.

---

## 4. Lambda Trigger: `app/services/lambda_trigger_glue.py`

**Propósito:** Função Lambda que aciona o job de refinamento quando arquivos são salvos no S3.

### Dependências

```python
import boto3
import json
```

### Função `lambda_handler(event, context)`

#### Parâmetros

- `event`: Dicionário com informações do evento S3
- `context`: Contexto da execução Lambda (não utilizado)

#### Fluxo de Execução

1. **Extração de Metadados:**
   - Bucket: `record["s3"]["bucket"]["name"]`
   - Key: `record["s3"]["object"]["key"]`

2. **Configuração do Job:**
   - `job_name = "glue_refined_spark"`
   - `args = {"--input_file": f"s3://{bucket}/{key}"}`

3. **Execução:**
   - Cria cliente Glue via `boto3.client("glue")`
   - Chama `start_job_run()` com nome do job e argumentos
   - Extrai `JobRunId` da resposta

4. **Logging:**
   - Imprime informações do job iniciado
   - Retorna resposta JSON com status 200 ou 500

#### Tratamento de Erros

- Captura todas as exceções em bloco try/except
- Retorna status 500 com mensagem de erro em caso de falha

---

## 5. Glue Job de Refinamento: `app/services/glue_refined.py`

**Propósito:** Processa dados brutos, compara com partição anterior e gera dados refinados usando Apache Spark.

### Imports e Configuração

```python
import sys
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.window import Window
```

### Argumentos do Job

- `JOB_NAME`: Nome do job Glue
- `input_file`: Caminho S3 do arquivo que acionou o processamento

### Funções Auxiliares

#### `extract_date_from_path(path: str) -> str`
- **Parâmetro:** Caminho S3 do arquivo
- **Retorno:** Data extraída no formato YYYY-MM-DD
- **Funcionalidade:** Usa regex para extrair data da partição `anomesdia=YYYY-MM-DD`

#### `get_last_file_from_partition(s3_path: str) -> str`
- **Parâmetro:** Caminho base da partição
- **Retorno:** Caminho S3 do arquivo mais recente ou None
- **Funcionalidade:**
  - Lista objetos no prefixo da partição
  - Filtra arquivos .parquet
  - Retorna o mais recente baseado em `LastModified`

### Fluxo de Processamento

1. **Decodificação do Input:**
   - `decoded_input_file = urllib.parse.unquote(args['input_file'])`

2. **Extração de Datas:**
   - `current_date_str = extract_date_from_path(decoded_input_file)`
   - `previous_date = current_date - timedelta(days=1)`

3. **Carregamento de Dados:**
   - **Arquivo Atual:** `spark.read.parquet(decoded_input_file)`
   - **Arquivo Anterior:** `get_last_file_from_partition(previous_partition)` (se existir)

4. **Transformações:**
   - Renomeia colunas: `codigo` → `ticker`, `qtde_teorica` → `n_acoes_teoricas`
   - Adiciona coluna `anomesdia`
   - Junta datasets atual + anterior (se disponível)

5. **Cálculo de Diferenças:**
   - Define janela por `ticker`, `acao`, `tipo` ordenada por `anomesdia`
   - `diff_part_pct = part_pct - lag(part_pct)`

6. **Categorização:**
   - `nivel_participacao` baseado em faixas de `part_pct`

7. **Saída:**
   - Converte para `DynamicFrame`
   - Configura sink para S3 + catálogo Glue
   - Particiona por `anomesdia`, `ticker`
   - Salva na tabela `acoes_refined`

### Dependências Externas

- **GlueContext:** Para operações Glue (sinks, catálogos)
- **SparkContext/SparkSession:** Para processamento distribuído
- **DynamicFrame:** Para integração com catálogo Glue/Athena
- **boto3:** Para operações S3 (listar objetos)

---

## 6. Utilitários: `app/utils/`

### `constants.py`

```python
S3_PATH = ""
```

- Define constantes globais (atualmente apenas S3_PATH vazio)

### `data_cleaners.py`

#### `clean_number(value: str) -> int`
- Remove pontos, espaços e converte para int
- Retorna 0 em caso de erro

#### `clean_percentage(value: str) -> float`
- Remove '%' e converte vírgula para ponto
- Retorna 0.0 em caso de erro

#### `clean_text(value: str) -> str`
- Remove espaços extras das extremidades
- Junta múltiplos espaços internos

---

## Fluxo de Dados Entre Componentes

1. **`run_scraper.py`** → **`scraper_ibov_day.py`**
   - Chama `main()` que instancia `IBOVScraper` e executa `run()`

2. **`glue_extract_data.py`** (Glue Job)
   - Mesmo fluxo de `IBOVScraper`, mas salva no S3
   - Dados vão para `s3://mlet8-fase2-pos/mlte8-scraping/`

3. **Evento S3** → **`lambda_trigger_glue.py`**
   - Evento PUT no bucket aciona Lambda
   - Lambda extrai metadados e inicia `glue_refined_spark`

4. **`glue_refined.py`** (Glue Job Spark)
   - Recebe `--input_file` como argumento
   - Carrega dados atuais e anteriores
   - Processa, transforma e salva na tabela `acoes_refined`

## Considerações para Desenvolvimento

- **Reutilização de Código:** `IBOVScraper` é duplicado entre arquivos locais e Glue
- **Tratamento de Erros:** Todos os componentes têm try/catch básicos
- **Logging:** Usa `logging` padrão do Python
- **Configuração:** Parâmetros hardcoded (URLs, caminhos S3)
- **Testabilidade:** Funções puras facilitam testes unitários
- **Performance:** Jobs Glue usam Spark para processamento distribuído

Este guia detalhado permite que desenvolvedores entendam não apenas o "o quê", mas o "como" cada componente funciona no pipeline ETL.