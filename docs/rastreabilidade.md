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
| Pagina Previsao | Esqueleto em `app/pages/4_Previsao.py`; conteudo e entrega da Sprint 4 (consome saida do modelo) | parcial |

## Sprint 4 - Storytelling e Modelo Preditivo

Pendente - inicia no bloco 4.
