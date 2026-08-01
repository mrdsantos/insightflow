# InsightFlow

Ciclo end-to-end de dados para um e-commerce simulado: geracao de dados brutos sujos,
ETL com quarentena para PostgreSQL, analises em SQL, dashboard Streamlit multipagina e
modelo preditivo de faturamento. Construido para o desafio Data Analytics do Programa
Desenvolve.

Dashboard publico: link adicionado apos o deploy.

## Resultados em numeros

- 8.209 linhas brutas no CSV; 7.643 chegam ao fato, 445 (5,4%) vao para quarentena com
  motivo registrado, 121 duplicatas descartadas.
- R$ 6,07 milhoes de faturamento concretizado em 24 meses, com sazonalidade forte de
  Black Friday (nov/2025 = R$ 500 mil, perto do dobro de um mes tipico).
- 8 de 30 produtos concentram 80% do faturamento; o top 10% dos clientes concentra
  41,4% da receita; RFM nomeia 10 segmentos sobre 580 clientes ativos.
- Previsao para jul/2026: ~R$ 321 mil (banda 207-435 mil). No teste temporal o baseline
  de media movel bateu a regressao por pouco e ambos tiveram R2 negativo - o resultado
  esta publicado como e, com a leitura critica no notebook 03 e na pagina de Previsao.

A narrativa completa esta em [docs/storytelling.md](docs/storytelling.md).

## Arquitetura

```
gerador (seed fixa) -> dados/ecom_data.csv -> ETL (pandas + psycopg)
    -> PostgreSQL: staging -> dw (star schema + quarentena)
    -> views SQL versionadas (sql/views/)
    -> Streamlit multipagina (app/)
```

Cada camada le apenas a anterior. O dashboard nao roda logica analitica propria: janela,
quintil, percentual acumulado e churn vivem nas views; as paginas so filtram e agregam
trivialmente. Star schema em `dw`: `dim_cliente`, `dim_produto`, `dim_localidade`,
`dim_calendario`, `fato_vendas`, mais a tabela `quarentena` (registro rejeitado inteiro
em JSONB + motivo). O modelo preditivo materializa `previsao_mensal` e `metricas_modelo`,
lidas pelo app via views como todo o resto.

## Metodologia

**Dados.** O enunciado pede um CSV simulado; o gerador (`src/gerador/`) produz 8.209
linhas com seed fixa e sujeira parametrizada (nulos, duplicatas, quantidade negativa,
datas e moedas em formatos mistos, variantes de caixa/acento, outliers de preco), para o
ETL ter o que limpar de verdade. O CSV esta commitado e e reproduzivel byte a byte.

**ETL (Sprint 1).** Full refresh idempotente: rodar duas vezes produz contagens
identicas. Validacao antes de carga; registro invalido nao e descartado em silencio,
vai para `dw.quarentena` com o motivo. Um relatorio de qualidade
([docs/relatorio_qualidade.md](docs/relatorio_qualidade.md)) e regenerado a cada
execucao. Funcoes puras de limpeza cobertas por pytest.

**EDA e SQL (Sprint 2).** Estatisticas descritivas, correlacao (Pearson vs Spearman) e
outliers (IQR vs z-score, com justificativa) no notebook 02. As metricas de negocio
viram views com window functions: RFM por `NTILE(5)`, retencao por coorte, Pareto com
acumulado, crescimento MoM/YoY por `LAG`. Definicoes que exigiram decisao (venda
concretizada, churn de 90 dias) estao em [docs/decisoes.md](docs/decisoes.md).

**Dashboard (Sprint 3).** Quatro paginas orientadas a pergunta de negocio, filtros
globais na sidebar com estado preservado entre paginas, paleta unica validada em
`app/theme.py`, todo grafico com gemeo tabular. Sem eixo duplo; o unico tracejado do
projeto e a projecao do modelo, onde tracejado significa projecao.

**Modelo (Sprint 4).** Serie mensal de faturamento, split temporal (18 meses de treino,
6 de teste), baseline de media movel de 3 meses contra regressao linear com tendencia e
dummies de mes, comparados por MAE, MAPE e R2. `src/modelo/treinar.py` replica o
notebook de forma reprodutivel e materializa o resultado no banco.

## Como executar

Requisitos: Python 3.13, PostgreSQL 18 (ou Docker).

### Local (venv)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env    # e ajuste a DATABASE_URL
python scripts/migrate.py         # cria database, DDL e views
python -m src.etl.pipeline        # CSV -> staging -> dw
python -m src.modelo.treinar      # treina e materializa a previsao
streamlit run app/Home.py
```

Testes: `pytest -q`. Para regenerar o CSV (opcional, o commitado e identico):
`python -m src.gerador.gerar_dados`.

### Docker

```bash
docker compose up --build
```

Sobe Postgres, aplica migracoes, roda ETL e treino, e serve o dashboard em
`http://localhost:8501`.

## Estrutura do repositorio

```
src/gerador/      gerador do CSV sujo (seed fixa)
src/etl/          pipeline: validacao, limpeza, carga
src/modelo/       treino e materializacao da previsao
scripts/          migrate.py (database + DDL + views, idempotente)
sql/ddl/          esquemas, dimensoes, fato, quarentena, tabelas do modelo
sql/views/        12 views consumidas pelo dashboard (contrato de dados)
sql/consultas/    SQL de apoio dos notebooks
notebooks/        01 qualidade, 02 EDA, 03 modelo
app/              Streamlit multipagina (theme, dados, filtros, ui, paginas)
tests/            pytest das funcoes puras de limpeza
docs/             decisoes, storytelling, rastreabilidade, contrato de dados
dados/            ecom_data.csv commitado
```

## Escopo do desafio

As quatro sprints do enunciado estao cobertas; o mapeamento requisito a requisito, com
arquivo e evidencia de cada item, esta em
[docs/rastreabilidade.md](docs/rastreabilidade.md).

| Sprint | Entrega |
|---|---|
| 1 - Ingestao e ETL | `src/etl/`, `scripts/migrate.py`, `sql/ddl/`, notebook 01 |
| 2 - EDA e SQL | notebook 02, `sql/views/`, `sql/consultas/` |
| 3 - Dashboard | `app/` (4 paginas, KPIs, sazonalidade, filtros dinamicos) |
| 4 - Storytelling e modelo | notebook 03, `src/modelo/`, `docs/storytelling.md` |

## Alem do escopo

Itens que o enunciado nao pede, construidos por decisao propria:

- **Quarentena com motivo**: linha invalida nao some, fica auditavel em `dw.quarentena`.
- **Relatorio de qualidade automatico**: o pipeline regenera o antes/depois da limpeza
  a cada execucao.
- **Contrato de dados** ([docs/contrato-dados.md](docs/contrato-dados.md)): tabela que
  liga cada elemento de tela a view que o alimenta - nenhuma view orfa, nenhum elemento
  sem fonte.
- **Coluna `ID_Pedido` no gerador**: desvio consciente do enunciado para dar nocao de
  pedido a base (registrado em [docs/decisoes.md](docs/decisoes.md)).
- **Registro de decisoes**: cada escolha questionavel tem secao propria em
  `docs/decisoes.md`, com o porque.
