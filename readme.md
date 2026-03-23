# Tech Challenge II FASE

## Estrutura do Projeto

```
├── app/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── glue_extract_data.py    # Glue Job de Extração
│   │   ├── glue_refined.py         # Glue Job de Refinamento
│   │   └── lambda_trigger_glue.py  # Function Lambda
│   └── utils/
│       ├── __init__.py
│       ├── constants.py
│       └── data_cleaners.py        # Funções de limpeza de dados
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
└── requirements.txt             # Dependências Python
```

## Funcionalidades

- **Glue Job Extract**: Extrai dados completos do portfólio diário do IBOV da B3
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

### Componentes principais
- **glue_extract_data.py**: Glue Job para coleta e extração de dados do IBOV (schedulado diariamente)
- **glue_refined.py**: Glue Job Spark que refina os dados e compara com partição anterior
- **lambda_trigger_glue.py**: Function Lambda acionada por eventos S3, responsável por iniciar o glue_refined_spark Job

### Serviços AWS criados

- glue_refined_spark - Spark - Script
- glue_extract_data - Python shell - Script
- lambda-glue-trigger

### Buckets S3 utilizados

- s3://mlet8-fase2-pos/athena-mlet8/
- s3://mlet8-fase2-pos/mlte8-scraping/
- s3://mlet8-fase2-pos/output_glue/refined/


# Links uteis 

Apresentacao : 
https://docs.google.com/presentation/d/1SqqSkTNXWJ_eD03MGPfhx81509R4FvX-NmOdm7pXniM/edit?usp=sharing

