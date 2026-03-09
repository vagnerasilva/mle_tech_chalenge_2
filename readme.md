# Tech Challenge II FASE

## Estrutura do Projeto

```
├── app/
│   ├── __init__.py
│   ├── routers/
│   │   └── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── glue_extract_data.py
│   │   ├── glue_refined.py
│   │   ├── lambda_trigger_glue.py
│   │   └── scraper_ibov_day.py  # Scraper do IBOV
│   └── utils/
│       ├── __init__.py
│       ├── constants.py
│       └── data_cleaners.py     # Funções de limpeza de dados
├── data_exec/
│   ├── anomesdia=2026-03-02/
│   └── anomesdia=2026-03-06/
├── terraform/
│   ├── main.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── terraform.tfvars
│   ├── variables.tf
│   └── modules/
│       └── start_glue/
│           ├── main.tf
│           ├── outputs.tf
│           └── variables.tf
├── dados.json
├── dados2.json
├── ibov_day_portfolio.json
├── pytest.ini
├── readme.md
├── requirements.txt             # Dependências Python
└── run_scraper.py               # Script principal para executar o scraper
```

## Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Instalar Browsers do Playwright
```bash
python3 -m playwright install
```

### 3. Executar o Scraper
```bash
python3 run_scraper.py
```

## Funcionalidades

- **Scraper IBOV**: Extrai dados completos do portfólio diário do IBOV da B3
- **Paginação Automática**: Coleta TODAS as páginas de forma automática
- **Limpeza de Dados**: Normalização de números, percentuais e textos
- **Output PARQUET**: Gera arquivo estruturado com todos os dados
- **Robustez**: Retry, timeout, logs e validação

## Output

O scraper gera o arquivo `.parquet` contendo:
- `codigo`: Código do ativo
- `acao`: Nome da empresa
- `tipo`: Tipo da ação
- `qtde_teorica`: Quantidade teórica (número inteiro)
- `part_pct`: Participação percentual (float)

## Informações úteis

### Os scripts estão na pasta de serviços
- glue_extract_data.py 
É o primeiro glue, o que precisa ser schedulado diariamente
- glue_refined.py
É o glue que faz o refinamento da tabela e comparação com partição anterior
- lambda_trigger_glue.py
Responsável por identificar o arquivo parquet que acionou a lambda e startar o ultimo glue job.

### Serviços criados

- glue_refined_spark - Spark - Script
- glue_extract_data - Python shell - Script
- lambda-glue-trigger

- s3://mlet8-fase2-pos/athena-mlet8/
- s3://mlet8-fase2-pos/mlte8-scraping/
- s3://mlet8-fase2-pos/output_glue/refined/