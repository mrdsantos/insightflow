# InsightFlow

Ciclo end-to-end de dados para um e-commerce simulado: geração de dados brutos sujos,
ETL com quarentena para PostgreSQL, análises em SQL, dashboard Streamlit multipágina e
modelo preditivo de faturamento. Construído para o desafio Data Analytics do Projeto
Desenvolve.

Dashboard público: https://insightflow.maiconsantos.com.br/

## Resultados em números

- 8.209 linhas brutas no CSV; 7.643 chegam ao fato, 445 (5,4%) vão para quarentena com
  motivo registrado, 121 duplicatas descartadas.
- R$ 6,07 milhões de faturamento concretizado em 24 meses, com sazonalidade forte de
  Black Friday (nov/2025 = R$ 500 mil, perto do dobro de um mês típico).
- 8 de 30 produtos concentram 80% do faturamento; o top 10% dos clientes concentra
  41,4% da receita; RFM nomeia 10 segmentos sobre 580 clientes ativos.
- Previsão para jul/2026: ~R$ 321 mil (banda 207-435 mil). No teste temporal o baseline
  de média móvel bateu a regressão por pouco e ambos tiveram R2 negativo - o resultado
  está publicado como é, com a leitura crítica no notebook 03 e na página de Previsão.

A narrativa completa está em [docs/storytelling.md](docs/storytelling.md).

## Arquitetura

```
gerador (seed fixa) -> dados/ecom_data.csv -> ETL (pandas + psycopg)
    -> PostgreSQL: staging -> dw (star schema + quarentena)
    -> views SQL versionadas (sql/views/)
    -> Streamlit multipagina (app/)
```

Cada camada lê apenas a anterior. O dashboard não roda lógica analítica própria: janela,
quintil, percentual acumulado e churn vivem nas views; as páginas só filtram e agregam
trivialmente. Star schema em `dw`: `dim_cliente`, `dim_produto`, `dim_localidade`,
`dim_calendario`, `fato_vendas`, mais a tabela `quarentena` (registro rejeitado inteiro
em JSONB + motivo). O modelo preditivo materializa `previsao_mensal` e `metricas_modelo`,
lidas pelo app via views como todo o resto.

## Metodologia

**Dados.** O enunciado pede um CSV simulado; o gerador (`src/gerador/`) produz 8.209
linhas com seed fixa e sujeira parametrizada (nulos, duplicatas, quantidade negativa,
datas e moedas em formatos mistos, variantes de caixa/acento, outliers de preço), para o
ETL ter o que limpar de verdade. O CSV está commitado e é reproduzível byte a byte.

**ETL (Sprint 1).** Full refresh idempotente: rodar duas vezes produz contagens
idênticas. Validação antes de carga; registro inválido não é descartado em silêncio,
vai para `dw.quarentena` com o motivo. Um relatório de qualidade
([docs/relatorio_qualidade.md](docs/relatorio_qualidade.md)) é regenerado a cada
execução. Funções puras de limpeza cobertas por pytest.

**EDA e SQL (Sprint 2).** Estatísticas descritivas, correlação (Pearson vs Spearman) e
outliers (IQR vs z-score, com justificativa) no notebook 02. As métricas de negócio
viram views com window functions: RFM por `NTILE(5)`, retenção por coorte, Pareto com
acumulado, crescimento MoM/YoY por `LAG`. Definições que exigiram decisão (venda
concretizada, churn de 90 dias) estão em [docs/decisoes.md](docs/decisoes.md).

**Dashboard (Sprint 3).** Cinco páginas orientadas à pergunta de negócio, filtros
globais na sidebar com estado preservado entre páginas, paleta validada em modo claro e
escuro em `app/theme.py` (o modo vem do sistema, com toggle na sidebar), todo gráfico com
gêmeo tabular. Sem eixo duplo; o único tracejado do
projeto é a projeção do modelo, onde tracejado significa projeção. A definição fica ao
lado do número: cada KPI tem tooltip e cada gráfico tem uma frase de leitura abaixo,
com a referência completa na página Definições.

**Modelo (Sprint 4).** Série mensal de faturamento, split temporal (18 meses de treino,
6 de teste), baseline de média móvel de 3 meses contra regressão linear com tendência e
dummies de mês, comparados por MAE, MAPE e R2. `src/modelo/treinar.py` replica o
notebook de forma reprodutível e materializa o resultado no banco.

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

Testes: `pytest -q`. Para regenerar o CSV (opcional, o commitado é idêntico):
`python -m src.gerador.gerar_dados`.

### Docker

```bash
docker compose up --build
```

Sobe Postgres, aplica migrações, roda ETL e treino, e serve o dashboard em
`http://localhost:8501`.

## Estrutura do repositório

```
src/gerador/      gerador do CSV sujo (seed fixa)
src/etl/          pipeline: validacao, limpeza, carga
src/modelo/       treino e materializacao da previsao
scripts/          migrate.py (database + DDL + views, idempotente)
sql/ddl/          esquemas, dimensoes, fato, quarentena, tabelas do modelo
sql/views/        12 views consumidas pelo dashboard, prefixadas na ordem de dependencia
sql/consultas/    SQL de apoio dos notebooks
notebooks/        01 qualidade, 02 EDA, 03 modelo
app/              Streamlit multipagina (theme, dados, filtros, ui, definicoes, paginas)
tests/            pytest das funcoes puras de limpeza, da ordem das views, do modulo
                  de definicoes e smoke de renderizacao das paginas
docs/             decisoes, storytelling, rastreabilidade, contrato de dados
dados/            ecom_data.csv commitado
```

## Escopo do desafio

As quatro sprints do enunciado estão cobertas; o mapeamento requisito a requisito, com
arquivo e evidência de cada item, está em
[docs/rastreabilidade.md](docs/rastreabilidade.md).

| Sprint | Entrega |
|---|---|
| 1 - Ingestão e ETL | `src/etl/`, `scripts/migrate.py`, `sql/ddl/`, notebook 01 |
| 2 - EDA e SQL | notebook 02, `sql/views/`, `sql/consultas/` |
| 3 - Dashboard | `app/` (5 páginas, KPIs, sazonalidade, filtros dinâmicos) |
| 4 - Storytelling e modelo | notebook 03, `src/modelo/`, `docs/storytelling.md` |

## Além do escopo

Itens que o enunciado não pede, construídos por decisão própria:

- **Quarentena com motivo**: linha inválida não some, fica auditável em `dw.quarentena`.
- **Relatório de qualidade automático**: o pipeline regenera o antes/depois da limpeza
  a cada execução.
- **Contrato de dados** ([docs/contrato-dados.md](docs/contrato-dados.md)): tabela que
  liga cada elemento de tela à view que o alimenta - nenhuma view órfã, nenhum elemento
  sem fonte.
- **Coluna `ID_Pedido` no gerador**: desvio consciente do enunciado para dar noção de
  pedido à base (registrado em [docs/decisoes.md](docs/decisoes.md)).
- **Registro de decisões**: cada escolha questionável tem seção própria em
  `docs/decisoes.md`, com o porquê.
- **Modo escuro**: abre no modo do sistema operacional e o toggle no rodapé da sidebar
  troca. São duas paletas de passos próprios, cada uma validada contra a sua superfície
  (separação sob daltonismo e contraste), e não uma inversão automática da clara - a
  validação é o motivo de o modo escuro ter ficado de fora até agora, e ela foi feita
  antes de ele entrar. Quem escolhe o modo é o frontend do Streamlit, e o Python só
  pergunta qual saiu: era ele decidir por conta própria que deixava o fundo e o gráfico em
  modos diferentes. Números e o achado em [docs/decisoes.md](docs/decisoes.md).
- **Marca no topo da sidebar**: três linhas de mesma largura, acima do menu de páginas, nas
  cores da paleta e nos dois modos. É um SVG gerado em tempo de execução porque a posição só
  é alcançável pelo `st.logo`, que aceita imagem, e porque justificar as três linhas à mesma
  medida depende da fonte que o sistema entrega - o `textLength` do SVG resolve isso sem
  depender de medição prévia. O porquê de cada número em [docs/decisoes.md](docs/decisoes.md).
