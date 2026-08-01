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

Pendente - inicia no bloco 3.

## Sprint 4 - Storytelling e Modelo Preditivo

Pendente - inicia no bloco 4.
