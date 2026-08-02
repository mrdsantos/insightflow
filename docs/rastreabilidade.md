# Rastreabilidade requisito -> entrega

Cada requisito do enunciado com onde ele é cumprido no repositório. Atualizado ao fim de
cada sprint. Status: `ok` (entregue), `parcial`, `pendente`.

## Geração do dataset (requisito mínimo do enunciado)

| Requisito | Entrega | Status |
|---|---|---|
| CSV com no mínimo 5.000 linhas e colunas relevantes de e-commerce | `src/gerador/gerar_dados.py` gera `dados/ecom_data.csv` com 8.209 linhas, 24 meses, seed fixa | ok |
| Colunas sugeridas (ID_Transacao, Data_Venda, ID_Cliente, Nome_Produto, Categoria_Produto, Valor_Unitario, Quantidade, Localidade_Venda, Metodo_Pagamento, Status_Pedido) | Todas presentes no CSV; coluna extra `ID_Pedido` é desvio documentado em `docs/decisoes.md` | ok |

## Sprint 1 - Ingestão e ETL

| Requisito | Entrega | Status |
|---|---|---|
| 1. Tratar valores nulos, duplicados e inconsistentes | `src/etl/validacao.py` (`valida_e_limpa`): nulo em campo chave rejeita para `dw.quarentena` com motivo; duplicata de `id_transacao` mantém a primeira e loga; caixa/acento inconsistente normaliza via `src/etl/limpeza.py`. Evidência: `docs/relatorio_qualidade.md` | ok |
| 2. Padronizar formatos de dados (datas e moedas) | `src/etl/limpeza.py`: `parse_data_multiformato` (3 formatos), `parse_moeda_brasileira` (3 formas). Cobertos por `tests/test_limpeza.py` | ok |
| 3. Criar banco relacional e carregar por ETL | PostgreSQL, star schema em `sql/ddl/` aplicado por `scripts/migrate.py`; pipeline `python -m src.etl.pipeline` (extract `src/etl/carga.py`, transform `src/etl/validacao.py`, load full refresh idempotente) | ok |

## Sprint 2 - EDA e SQL

| Requisito | Entrega | Status |
|---|---|---|
| 1. Extrair estatísticas descritivas do conjunto de dados | `sql/consultas/q_descritivas.sql` (min/quartis/mediana/média/desvio por métrica) lida e discutida em `notebooks/02_eda.ipynb` | ok |
| 2. Consultas SQL complexas com Joins, Window Functions e Group By | Joins do star schema em `dw.vw_vendas`; window functions: LAG (`vw_kpis_mensais`, `vw_crescimento_categoria`, `q_yoy.sql`), NTILE (`vw_rfm`, `vw_receita_top_clientes`), MIN OVER (`vw_coorte_retencao`), SUM OVER + ROW_NUMBER (`vw_pareto_produtos`), FILTER (`vw_produtos_metricas`); GROUP BY multigrão em `vw_faturamento_mensal`. Todas em `sql/views/`, aplicadas por `scripts/migrate.py` | ok |
| 3. Análise de correlação e identificação de outliers | Correlação Pearson x Spearman em dois grãos (item e cliente) e comparação IQR vs z-score em `notebooks/02_eda.ipynb` + `sql/consultas/q_outliers.sql`; critério escolhido registrado em `docs/decisoes.md` | ok |
| Pergunta de negócio: perfil de consumo e segmentação (ex: RFM) | `dw.vw_rfm` (NTILE(5), 10 segmentos nomeados) + `dw.vw_coorte_retencao`/`dw.vw_curva_retencao`; consumo na página Clientes no bloco 3 | ok |
| Base do dashboard da Sprint 3 (KPIs nomeados no enunciado) | `dw.vw_kpis_mensais`: Faturamento Total, Ticket Médio, Taxa de Retenção e Churn Rate mês a mês; definição de churn em `docs/decisoes.md` | ok |
| Contrato de dados tela -> view | `docs/contrato-dados.md`: 12 views, nenhuma órfã, nenhum elemento sem fonte | ok |

## Sprint 3 - Visualização e Dashboard

| Requisito | Entrega | Status |
|---|---|---|
| 1. Dashboard com KPIs principais (Faturamento Total, Ticket Médio, Churn Rate ou Taxa de Retenção) | Streamlit multipage em `app/`; `app/Home.py` traz os 4 KPIs em stat tiles com delta vs período anterior e sparkline, lidos de `dw.vw_kpis_mensais`. Páginas Clientes e Produtos com linhas de KPI próprias | ok |
| 2. Gráficos de séries temporais para análise de sazonalidade | `app/Home.py`: série de faturamento mensal (tendência) e sazonalidade ano a ano sobreposta (uma linha por ano); small multiples de MoM por categoria em `app/pages/3_Produtos.py` | ok |
| 3. Filtros dinâmicos para navegação e comparação de resultados | `app/filtros.py`: sidebar global (período com presets, categoria, UF, status) com estado preservado entre páginas via `st.session_state`; a navegação mantendo o recorte é a comparação. Views estruturais não reagem por decisão registrada em `docs/decisoes.md` e `docs/contrato-dados.md` | ok |
| Ferramenta de BI: bibliotecas Python (Streamlit/Dash) aceitas pelo enunciado | Streamlit + Plotly; corte do Power BI justificado em `docs/decisoes.md`. Tema e paleta centralizados em `app/theme.py` e `.streamlit/config.toml` | ok |
| extra: modo escuro com toggle na sidebar | Além do enunciado. `app/theme.py` com duas paletas de passos próprios, cada uma validada contra a sua superfície (daltonismo e contraste); `theme.paleta()` resolve por sessão e `ui.grafico()` aplica o template por figura; toggle no rodapé de `app/filtros.py`; `[theme.dark]` no `.streamlit/config.toml`. Quem escolhe o modo é o frontend, e `theme.paleta()` só pergunta qual saiu via `st.context.theme`: o padrão é o modo do sistema e o toggle sobrepõe por `embed_options`. Guardado por `tests/test_tema.py` e pelo smoke de `tests/test_paginas.py` nos dois modos. Números e justificativa em `docs/decisoes.md` | ok |
| Entrega 4: link público do dashboard | Publicado em https://insightflow.maiconsantos.com.br/ via Dokploy (Docker Swarm), imagem construída pelo `Dockerfile`; link no topo do README | ok |
| `st.cache_data` nas queries (requisito do plano) | `app/dados.py`: `ler_view` com `st.cache_data(ttl=600)` e engine única via `st.cache_resource` | ok |
| Página Previsão | `app/pages/4_Previsão.py` completa na Sprint 4: KPIs, histórico + ajuste + projeção tracejada com banda, tabela modelo vs baseline, leitura do resultado | ok |
| Explicabilidade dos números na própria tela | `app/definicoes.py` como fonte única do texto; tooltip nos 16 tiles de KPI, frase de leitura sob os 12 gráficos das páginas 1 a 3, e a página `app/pages/5_Definições.py` com definição de cada KPI, a grade dos 10 segmentos RFM e as limitações conhecidas. Motivo em `docs/decisoes.md`, seção "Quinta página, reabrindo o teto de quatro telas do plano"; guardado por `tests/test_definicoes.py` e `tests/test_paginas.py` | ok |

## Sprint 4 - Storytelling e Modelo Preditivo

| Requisito | Entrega | Status |
|---|---|---|
| 1. Modelo simples de Regressão Linear ou similar para previsão de vendas | `notebooks/03_modelo.ipynb`: regressão linear (tendência + dummies de mês) contra baseline de média móvel 3m, split temporal (18 meses treino, 6 teste), MAE/MAPE/R2 dos dois; `src/modelo/treinar.py` replica o notebook e materializa `dw.previsao_mensal` e `dw.metricas_modelo`, lidas por `dw.vw_previsao` e `dw.vw_metricas_modelo` | ok |
| 2. Documentar insights por storytelling analítico | `docs/storytelling.md`: narrativa em 5 atos (crescimento em degraus, Black Friday, concentração, segmentos RFM acionáveis, previsão com limites), cada um apontando a página do dashboard; fecha com recomendações | ok |
| 3. README final com metodologia, instruções e resultados | `README.md`: resultados em números, arquitetura, metodologia por sprint, execução local (venv) e Docker, escopo do desafio e além do escopo | ok |
| Pergunta de negócio: é possível prever vendas/faturamento do próximo mês? | Sim, como ordem de grandeza: jul/2026 ~R$ 321 mil, banda 207-435 mil. Resposta honesta sobre a confiança (R2 negativo no teste, baseline competitivo) na página Previsão, notebook 03 e `docs/decisoes.md` | ok |

## Entrega final (seção Entrega do enunciado)

| Item | Entrega | Status |
|---|---|---|
| 1. Repositório no GitHub | `github.com/mrdsantos/insightflow`, público, com PRs e milestones por sprint | ok |
| 2. Scripts e notebooks das Sprints 1, 2 e 4 | `src/`, `scripts/`, `sql/`, `notebooks/01`, `02`, `03` | ok |
| 3. requirements.txt e instruções de execução | `requirements.txt` (versões pinadas) + seção Como executar do README | ok |
| 4. Link público ou dashboard local | Link público em https://insightflow.maiconsantos.com.br/; dashboard local via venv ou `docker compose up --build` | ok |
| 5. Dados: CSV e script de geração | `dados/ecom_data.csv` commitado + `src/gerador/gerar_dados.py` com seed fixa | ok |

## Critérios de avaliação

| Critério (peso) | Onde está a evidência |
|---|---|
| Qualidade do ETL (30%) | `src/etl/` (validação com quarentena por motivo, limpeza multiformato, full refresh idempotente), `sql/ddl/` (star schema com PKs, FKs, índices), `docs/relatorio_qualidade.md`, `tests/test_limpeza.py`, `tests/test_ordem_views.py` (valida estaticamente a ordem das views, sem banco) |
| Análise de Dados (35%) | Notebooks 01-03; window functions em `sql/views/` (LAG, NTILE, SUM OVER, FILTER); correlação e outliers com escolha justificada; RFM, coorte e churn definidos a partir dos dados; modelo com baseline e leitura crítica |
| Visualização (25%) | `app/`: 5 páginas orientadas à pergunta, KPIs do enunciado, séries com sazonalidade, filtros globais persistentes, paleta validada em modo claro e escuro, gêmeo tabular em todo gráfico, sem eixo duplo; explicabilidade na própria tela (tooltip em cada KPI, frase de leitura sob cada gráfico, página Definições); marca tipográfica no topo da sidebar (`ui.marca`, `tests/test_marca.py`) |
| Documentação (10%) | `README.md`, `docs/storytelling.md`, `docs/decisoes.md`, `docs/contrato-dados.md`, este arquivo, e a documentação dentro do produto: `app/definicoes.py` alimentando os tooltips e a página Definições |
