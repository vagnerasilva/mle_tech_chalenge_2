# Roteiro de Apresentação: Tech Challenge II - Pipeline ETL IBOV (10 minutos)

## 🎯 ESTRUTURA GERAL
**Duração Total:** 10 minutos
**Objetivo:** Apresentar solução completa atendendo todos os requisitos do desafio
**Tom:** Técnico mas acessível, focado em resultados

---

## 📋 SEÇÃO 1: INTRODUÇÃO (1:30 min)
**Tempo:** 0:00 - 1:30

### Apresentação Pessoal (0:15)
- "Olá, sou [Seu Nome], estudante de Engenharia de Dados"
- "Vou apresentar minha solução para o Tech Challenge II"

### Contexto do Desafio (1:15)
- **Problema:** "O desafio propõe construir um pipeline completo de dados para extrair, processar e analisar dados de ações da B3 usando AWS"
- **Fonte de Dados:** "Focamos no IBOV (Índice Bovespa) com granularidade diária"
- **Tecnologias:** "Utilizando S3, Glue, Lambda e Athena"

**Transição:** "Vamos ver como transformei esses requisitos em uma solução robusta"

---

## 🏗️ SEÇÃO 2: ARQUITETURA DA SOLUÇÃO (2:30 min)
**Tempo:** 1:30 - 4:00

### Visão Geral da Arquitetura (0:45)
- **Pipeline ETL:** "Criei um pipeline batch completo com 6 componentes principais"
- **Fluxo:** Scraper → Glue Extract → S3 → Lambda → Glue Refined → Athena
- **Mostrar diagrama Mermaid** (já criado na documentação)

### Componentes Principais (1:45)
1. **Glue Job Extract** - Processamento e extração diária em AWS
2. **S3 Bucket** - Armazenamento com particionamento
3. **Lambda Function** - Orquestração automática
4. **Glue Job Refined** - Transformações avançadas com Spark
5. **Athena Table** - Consulta SQL dos dados refinados

**Transição:** "Agora vamos verificar como cada requisito foi atendido"

---

## ✅ SEÇÃO 3: REQUISITOS ATENDIDOS (4:00 min)
**Tempo:** 4:00 - 8:00

### Requisitos 1-4: Extração e Ingestão (1:30)
- **✅ Req 1:** "Scraping diário do IBOV via API da B3"
- **✅ Req 2:** "Dados em Parquet particionado por data (anomesdia)"
- **✅ Req 3:** "Bucket S3 aciona Lambda automaticamente"
- **✅ Req 4:** "Lambda em Python inicia job Glue"

### Requisitos 5-8: Processamento e Análise (2:30)
- **✅ Req 5:** Transformações obrigatórias implementadas:
  - **Agrupamento:** Contagem e soma de ações por categoria
  - **Renomeação:** `codigo`→`ticker`, `qtde_teorica`→`n_acoes_teoricas`
  - **Cálculo Temporal:** `diff_part_pct` (diferença de participação entre dias)

- **✅ Req 6:** "Dados refinados particionados por data e ticker"
- **✅ Req 7:** "Catálogo automático no Glue Catalog (tabela acoes_refined)"
- **✅ Req 8:** "Consultas SQL via Athena funcionando"

**Transição:** "Vamos ver alguns detalhes técnicos interessantes"

---

## 🔧 SEÇÃO 4: HIGHLIGHTS TÉCNICOS (1:30 min)
**Tempo:** 8:00 - 9:30

### Cálculo Diferencial Inteligente (0:45)
- **Lógica:** "Calculamos variação na participação das ações entre dias"
- **Técnica:** "Usando window functions do Spark para comparar períodos"
- **Valor:** "Identifica tendências e rebalanceamentos do índice"

### Categorização Automática (0:45)
- **Regras:** Pequena (≤0.1%), Média (0.1-1%), Grande (>1%)
- **Aplicação:** "Segmenta ações por tamanho e impacto no IBOV"
- **Benefício:** "Facilita análise de risco e estratégias de investimento"

---

## 🎉 SEÇÃO 5: CONCLUSÃO (0:30 min)
**Tempo:** 9:30 - 10:00

### Resultados Alcançados (0:20)
- "✅ Todos os 8 requisitos foram implementados com sucesso"
- "Pipeline automatizado e escalável na AWS"
- "Dados prontos para análise avançada via SQL"

### Próximos Passos (0:10)
- "O pipeline está pronto para produção"
- "Pode ser facilmente expandido para outros índices"

**Encerramento:** "Obrigado pela atenção! Alguma pergunta?"

---

## 📊 APOIO VISUAL RECOMENDADO

### Slides/Chaves Visuais:
1. **Slide 1:** Título + Seu nome
2. **Slide 2:** Lista dos 8 requisitos do desafio
3. **Slide 3:** Diagrama de arquitetura (Mermaid)
4. **Slide 4:** Tabela comparativa "Requisito vs Implementação"
5. **Slide 5:** Exemplo dos cálculos diferenciais
6. **Slide 6:** Demonstração Athena (print screen)
7. **Slide 7:** Conclusão + Q&A

### Dicas de Apresentação:
- **Ritmo:** Falar pausadamente, fazer pausas para mudança de slide
- **Ênfase:** Destacar "✅" quando mencionar requisitos atendidos
- **Demonstração:** Mostrar código rapidamente se houver tempo
- **Interação:** Perguntar se audiência está acompanhando

### Backup de Tempo:
- Se passar 10 min: Cortar detalhes técnicos
- Se sobrar tempo: Mostrar mais do código ou diagramas

---

**⏱️ CRONOMETRAGEM DETALHADA:**
- Introdução: 1:30
- Arquitetura: 2:30
- Requisitos: 4:00
- Técnico: 1:30
- Conclusão: 0:30
**TOTAL: 10:00**</content>
<parameter name="filePath">/Users/vagnerantononiodasilva/Documents/projetos/mle_tech_chalenge_2/presentation_script_10min.md