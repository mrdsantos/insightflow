# Rastreabilidade requisito -> entrega

Cada requisito do enunciado com onde ele e cumprido no repositorio. Atualizado ao fim de
cada sprint. Status: `ok` (entregue), `parcial`, `pendente`.

## Geracao do dataset (requisito minimo do enunciado)

| Requisito | Entrega | Status |
|---|---|---|
| CSV com no minimo 5.000 linhas e colunas relevantes de e-commerce | `src/gerador/gerar_dados.py` gera `dados/ecom_data.csv` com 8.209 linhas, 24 meses, seed fixa | ok |
| Colunas sugeridas (ID_Transacao, Data_Venda, ID_Cliente, Nome_Produto, Categoria_Produto, Valor_Unitario, Quantidade, Localidade_Venda, Metodo_Pagamento, Status_Pedido) | Todas presentes no CSV; coluna extra `ID_Pedido` e desvio documentado em `docs/decisoes.md` | ok |

## Sprint 1 - Ingestao e ETL

| Requisito | Entrega | Status |
|---|---|---|
| 1. Tratar valores nulos, duplicados e inconsistentes | `src/etl/validacao.py` (`valida_e_limpa`): nulo em campo chave rejeita para `dw.quarentena` com motivo; duplicata de `id_transacao` mantem a primeira e loga; caixa/acento inconsistente normaliza via `src/etl/limpeza.py`. Evidencia: `docs/relatorio_qualidade.md` | ok |
| 2. Padronizar formatos de dados (datas e moedas) | `src/etl/limpeza.py`: `parse_data_multiformato` (3 formatos), `parse_moeda_brasileira` (3 formas). Cobertos por `tests/test_limpeza.py` | ok |
| 3. Criar banco relacional e carregar por ETL | PostgreSQL, star schema em `sql/ddl/` aplicado por `scripts/migrate.py`; pipeline `python -m src.etl.pipeline` (extract `src/etl/carga.py`, transform `src/etl/validacao.py`, load full refresh idempotente) | ok |

## Sprint 2 - EDA e SQL

| Requisito | Entrega | Status |
|---|---|---|
| 1. Extrair estatisticas descritivas do conjunto de dados | `sql/consultas/q_descritivas.sql` (min/quartis/mediana/media/desvio por metrica) lida e discutida em `notebooks/02_eda.ipynb` | ok |
| 2. Consultas SQL complexas com Joins, Window Functions e Group By | Joins do star schema em `dw.vw_vendas`; window functions: LAG (`vw_kpis_mensais`, `vw_crescimento_categoria`, `q_yoy.sql`), NTILE (`vw_rfm`, `vw_receita_top_clientes`), MIN OVER (`vw_coorte_retencao`), SUM OVER + ROW_NUMBER (`vw_pareto_produtos`), FILTER (`vw_produtos_metricas`); GROUP BY multi-grao em `vw_faturamento_mensal`. Todas em `sql/views/`, aplicadas por `scripts/migrate.py` | ok |
| 3. Analise de correlacao e identificacao de outliers | Correlacao Pearson x Spearman em dois graos (item e cliente) e comparacao IQR vs z-score em `notebooks/02_eda.ipynb` + `sql/consultas/q_outliers.sql`; criterio escolhido registrado em `docs/decisoes.md` | ok |
| Pergunta de negocio: perfil de consumo e segmentacao (ex: RFM) | `dw.vw_rfm` (NTILE(5), 10 segmentos nomeados) + `dw.vw_coorte_retencao`/`dw.vw_curva_retencao`; consumo na pagina Clientes no bloco 3 | ok |
| Base do dashboard da Sprint 3 (KPIs nomeados no enunciado) | `dw.vw_kpis_mensais`: Faturamento Total, Ticket Medio, Taxa de Retencao e Churn Rate mes a mes; definicao de churn em `docs/decisoes.md` | ok |
| Contrato de dados tela -> view | `docs/contrato-dados.md`: 12 views, nenhuma orfa, nenhum elemento sem fonte | ok |

## Sprint 3 - Visualizacao e Dashboard

| Requisito | Entrega | Status |
|---|---|---|
| 1. Dashboard com KPIs principais (Faturamento Total, Ticket Medio, Churn Rate ou Taxa de Retencao) | Streamlit multipage em `app/`; `app/Home.py` traz os 4 KPIs em stat tiles com delta vs periodo anterior e sparkline, lidos de `dw.vw_kpis_mensais`. Paginas Clientes e Produtos com linhas de KPI proprias | ok |
| 2. Graficos de series temporais para analise de sazonalidade | `app/Home.py`: serie de faturamento mensal (tendencia) e sazonalidade ano a ano sobreposta (uma linha por ano); small multiples de MoM por categoria em `app/pages/3_Produtos.py` | ok |
| 3. Filtros dinamicos para navegacao e comparacao de resultados | `app/filtros.py`: sidebar global (periodo com presets, categoria, UF, status) com estado preservado entre paginas via `st.session_state`; a navegacao mantendo o recorte e a comparacao. Views estruturais nao reagem por decisao registrada em `docs/decisoes.md` e `docs/contrato-dados.md` | ok |
| Ferramenta de BI: bibliotecas Python (Streamlit/Dash) aceitas pelo enunciado | Streamlit + Plotly; corte do Power BI justificado em `docs/decisoes.md`. Tema e paleta centralizados em `app/theme.py` e `.streamlit/config.toml` | ok |
| Entrega 4: link publico do dashboard | Dockerfile e docker-compose.yml prontos; deploy no Dokploy agendado (nao bloqueia o bloco 4) | parcial |
| `st.cache_data` nas queries (requisito do plano) | `app/dados.py`: `ler_view` com `st.cache_data(ttl=600)` e engine unica via `st.cache_resource` | ok |
| Pagina Previsao | `app/pages/4_Previsao.py` completa na Sprint 4: KPIs, historico + ajuste + projecao tracejada com banda, tabela modelo vs baseline, leitura do resultado | ok |

## Sprint 4 - Storytelling e Modelo Preditivo

| Requisito | Entrega | Status |
|---|---|---|
| 1. Modelo simples de Regressao Linear ou similar para previsao de vendas | `notebooks/03_modelo.ipynb`: regressao linear (tendencia + dummies de mes) contra baseline de media movel 3m, split temporal (18 meses treino, 6 teste), MAE/MAPE/R2 dos dois; `src/modelo/treinar.py` replica o notebook e materializa `dw.previsao_mensal` e `dw.metricas_modelo`, lidas por `dw.vw_previsao` e `dw.vw_metricas_modelo` | ok |
| 2. Documentar insights por storytelling analitico | `docs/storytelling.md`: narrativa em 5 atos (crescimento em degraus, Black Friday, concentracao, segmentos RFM acionaveis, previsao com limites), cada um apontando a pagina do dashboard; fecha com recomendacoes | ok |
| 3. README final com metodologia, instrucoes e resultados | `README.md`: resultados em numeros, arquitetura, metodologia por sprint, execucao local (venv) e Docker, escopo do desafio e alem do escopo | ok |
| Pergunta de negocio: e possivel prever vendas/faturamento do proximo mes? | Sim, como ordem de grandeza: jul/2026 ~R$ 321 mil, banda 207-435 mil. Resposta honesta sobre a confianca (R2 negativo no teste, baseline competitivo) na pagina Previsao, notebook 03 e `docs/decisoes.md` | ok |

## Entrega final (secao Entrega do enunciado)

| Item | Entrega | Status |
|---|---|---|
| 1. Repositorio no GitHub | `github.com/mrdsantos/insightflow`, publico, com PRs e milestones por sprint | ok |
| 2. Scripts e notebooks das Sprints 1, 2 e 4 | `src/`, `scripts/`, `sql/`, `notebooks/01`, `02`, `03` | ok |
| 3. requirements.txt e instrucoes de execucao | `requirements.txt` (versoes pinadas) + secao Como executar do README | ok |
| 4. Link publico ou dashboard local | Dashboard local via venv ou `docker compose up --build`; link publico via Dokploy | parcial |
| 5. Dados: CSV e script de geracao | `dados/ecom_data.csv` commitado + `src/gerador/gerar_dados.py` com seed fixa | ok |

## Criterios de avaliacao

| Criterio (peso) | Onde esta a evidencia |
|---|---|
| Qualidade do ETL (30%) | `src/etl/` (validacao com quarentena por motivo, limpeza multiformato, full refresh idempotente), `sql/ddl/` (star schema com PKs, FKs, indices), `docs/relatorio_qualidade.md`, `tests/test_limpeza.py`, `tests/test_ordem_views.py` (migracao aplica em banco zerado) |
| Analise de Dados (35%) | Notebooks 01-03; window functions em `sql/views/` (LAG, NTILE, SUM OVER, FILTER); correlacao e outliers com escolha justificada; RFM, coorte e churn definidos a partir dos dados; modelo com baseline e leitura critica |
| Visualizacao (25%) | `app/`: 4 paginas orientadas a pergunta, KPIs do enunciado, series com sazonalidade, filtros globais persistentes, paleta unica validada, gemeo tabular em todo grafico, sem eixo duplo |
| Documentacao (10%) | `README.md`, `docs/storytelling.md`, `docs/decisoes.md`, `docs/contrato-dados.md`, este arquivo |
