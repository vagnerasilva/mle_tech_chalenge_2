# Tech Challenge II FASE

## Estrutura do Projeto

```
├── app/
│   ├── __init__.py
│   ├── routers/
│   │   └── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── scraper_ibov_day.py  # Scraper do IBOV
│   └── utils/
│       ├── __init__.py
│       └── data_cleaners.py     # Funções de limpeza de dados
├── run_scraper.py               # Script principal para executar o scraper
├── requirements.txt             # Dependências Python
└── ibov_day_portfolio.json     # Output do scraper (gerado após execução)
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