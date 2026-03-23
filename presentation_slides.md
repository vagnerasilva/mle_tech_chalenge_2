# Slides de Apoio - Tech Challenge II (10 min)

## 📊 SLIDE 1: Título
```
TECH CHALLENGE II - PIPELINE ETL IBOV

Pipeline Batch Bovespa: Ingestão e Arquitetura de Dados

[Seu Nome]
Data: [Data da Apresentação]
```

---

## 📋 SLIDE 2: Contexto do Desafio
```
🎯 DESAFIO PROPOSTO

Construir pipeline completo para dados da B3 usando:
• AWS S3, Glue, Lambda e Athena
• Granularidade diária
• Scraping ou bibliotecas (yfinance)

📋 8 REQUISITOS PRINCIPAIS:
1. Scraping diário de ações/índices B3
2. Dados brutos em Parquet particionado no S3
3. Bucket S3 aciona Lambda
4. Lambda inicia job Glue
5. Job Glue com transformações específicas
6. Dados refinados particionados (data + código)
7. Catálogo automático no Glue Catalog
8. Consultas SQL via Athena
```

---

## 🏗️ SLIDE 3: Arquitetura da Solução
```
ARQUITETURA IMPLEMENTADA

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ glue_extract_   │ -> │   S3 Bucket     │ -> │ lambda_trigger_ │
│    data.py      │    │ mlte8-scraping  │    │    glue.py      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
Glue Job                Parquet Particionado   Função Lambda
Agendado Diário                                      │
                                                     ▼
                                             ┌─────────────────┐
                                             │ glue_refined.py │
                                             │    (Spark)      │
                                             └─────────────────┘
                                                     │
                                                     ▼
                                             ┌─────────────────┐
                                             │ Tabela Athena   │
                                             │ acoes_refined   │
                                             └─────────────────┘
```

---

## ✅ SLIDE 4: Requisitos Atendidos
```
STATUS DOS REQUISITOS

✅ REQ 1: Scraping IBOV diário via API B3
✅ REQ 2: Parquet particionado (anomesdia=YYYY-MM-DD)
✅ REQ 3: Evento S3 PUT → Lambda automática
✅ REQ 4: Lambda Python inicia Glue job
✅ REQ 5: Transformações Glue implementadas:
   • Agrupamento: Contagem por categoria
   • Renomeação: codigo→ticker, qtde_teorica→n_acoes_teoricas
   • Cálculo: diff_part_pct (diferença entre períodos)
✅ REQ 6: Particionamento data + ticker
✅ REQ 7: Catálogo Glue automático (tabela acoes_refined)
✅ REQ 8: Consultas SQL Athena funcionando
```

---

## 🔧 SLIDE 5: Cálculo Diferencial
```
CÁLCULO DIFERENCIAL - diff_part_pct

🎯 OBJETIVO:
Calcular variação na participação das ações entre dias

📊 LÓGICA TÉCNICA:
• Window Function Spark por (ticker, acao, tipo)
• diff_part_pct = part_pct_atual - part_pct_anterior
• Ordenação por anomesdia

📈 EXEMPLO PRÁTICO:
PETR4 - Participação:
• 01/01: 5.2% → diff = null (primeiro dia)
• 02/01: 5.5% → diff = +0.3% (aumentou)
• 03/01: 5.1% → diff = -0.4% (diminuiu)

💡 VALOR: Identifica tendências do mercado
```

---

## 📊 SLIDE 6: Categorização
```
CATEGORIZAÇÃO - nivel_participacao

📏 FAIXAS DEFINIDAS:
• PEQUENA: part_pct ≤ 0.1%
• MÉDIA: 0.1% < part_pct ≤ 1%
• GRANDE: part_pct > 1%

🏆 EXEMPLO REAL (IBOV):
GRANDES (>1%): VALE3 (8.2%), PETR4 (5.1%), ITUB4 (3.8%)
MÉDIAS (0.1-1%): BBDC4 (0.8%), ABEV3 (0.6%), WEGE3 (0.4%)
PEQUENAS (≤0.1%): GNDI3 (0.05%), ALPA4 (0.02%)

🎯 BENEFÍCIO: Análise de risco e estratégias
```

---

## 🗄️ SLIDE 7: Demonstração Athena
```
CONSULTAS SQL - ATHENA

-- Exemplo 1: Ações que mais ganharam participação
SELECT ticker, acao, diff_part_pct
FROM acoes_refined
WHERE diff_part_pct > 0
ORDER BY diff_part_pct DESC
LIMIT 10;

-- Exemplo 2: Distribuição por categoria
SELECT nivel_participacao, COUNT(*) as quantidade
FROM acoes_refined
GROUP BY nivel_participacao;

-- Exemplo 3: Evolução temporal
SELECT anomesdia, ticker, part_pct, diff_part_pct
FROM acoes_refined
WHERE ticker = 'PETR4'
ORDER BY anomesdia;
```

---

## 🎉 SLIDE 8: Conclusão
```
CONCLUSÃO

✅ TODOS OS 8 REQUISITOS ATENDIDOS
✅ PIPELINE AUTOMATIZADO E ESCALÁVEL
✅ DADOS PRONTOS PARA ANÁLISE AVANÇADA

🚀 PRÓXIMOS PASSOS:
• Expansão para outros índices
• Adição de métricas avançadas
• Dashboard em tempo real

💡 VALOR AGREGADO:
• Cálculos diferenciais inteligentes
• Categorização automática
• Arquitetura serverless na AWS

OBRIGADO!
```

---

## 🎨 DICAS DE DESIGN

### Cores Consistentes:
- **Azul claro:** Scripts locais (#e1f5fe)
- **Roxo claro:** Glue Jobs (#f3e5f5)
- **Verde claro:** S3/Storage (#e8f5e8)
- **Laranja claro:** Lambda (#fff3e0)
- **Rosa claro:** Spark (#fce4ec)

### Elementos Visuais:
- ✅ Checkmarks verdes para requisitos atendidos
- 📊 Gráficos simples para dados
- 🔄 Setas para fluxo de dados
- 📈 Ícones para métricas

### Fontes:
- **Títulos:** Bold, 32pt
- **Subtítulos:** Regular, 24pt
- **Corpo:** Regular, 18pt
- **Código:** Monospace, 14pt</content>
<parameter name="filePath">/Users/vagnerantononiodasilva/Documents/projetos/mle_tech_chalenge_2/presentation_slides.md