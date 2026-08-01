# Contrato de dados

Tabela que liga cada elemento de tela do dashboard à view SQL que o alimenta. Regras que ela
impõe: nenhuma view fora desta tabela será construída (view órfã) e nenhum elemento de tela
fica sem fonte. O app só aplica filtro (WHERE) e agregação trivial (soma, contagem, pivot);
toda lógica analítica (janelas, quintis, percentuais acumulados, definição de churn) vive nas
views versionadas em `sql/views/`.

| Página | Elemento | View / query | Granularidade | Colunas retornadas |
|---|---|---|---|---|
| 1 Visão Geral | Linha de 4 KPIs + deltas + sparklines | `vw_kpis_mensais` | mês | ano_mes, faturamento, pedidos, ticket_medio, clientes_ativos, clientes_novos, ticket_medio_cliente, taxa_retencao, churn_rate |
| 1 | Série temporal de faturamento | `vw_faturamento_mensal` | mês x categoria x uf x status | ano_mes, ano, mes, categoria, uf, status, faturamento, itens |
| 1 | Sazonalidade ano a ano | `vw_faturamento_mensal` (app separa por ano) | idem | idem |
| 1 | Barras por categoria (cor única) | `vw_faturamento_mensal` (app agrega) | idem | idem |
| 2 Clientes | Linha de KPIs | `vw_kpis_mensais` + `vw_receita_top_clientes` | mês / 1 linha | (acima) / pct_receita_top10 |
| 2 | Heatmap RFM (R x F) | `vw_rfm` (app pivota contagem) | cliente | id_cliente, recencia_dias, frequencia, monetario, score_r, score_f, score_m, segmento |
| 2 | Barras tamanho/receita por segmento | `vw_rfm` (app agrega) | cliente | idem |
| 2 | Dispersão Recência x Monetário (emphasis 3) | `vw_rfm` | cliente | idem |
| 2 | Matriz de coorte | `vw_coorte_retencao` | coorte x meses_desde | coorte_mes, meses_desde, clientes_coorte, clientes_retidos, pct_retido |
| 2 | Curva de retenção média | `vw_curva_retencao` | meses_desde | meses_desde, pct_medio |
| 3 Produtos | Linha de KPIs | `vw_vendas` (SKUs ativos, categoria líder via agregação trivial) + `vw_pareto_produtos` (produto líder, concentração) | item / produto | ver views |
| 3 | Pareto (% na mesma escala, sem eixo duplo) | `vw_pareto_produtos` | produto | produto, faturamento, pct_faturamento, pct_acumulado, posicao |
| 3 | Small multiples MoM por categoria | `vw_crescimento_categoria` | mês x categoria | ano_mes, categoria, faturamento, mom_pct |
| 3 | Matriz crescimento x faturamento (emphasis 3) | `vw_produtos_metricas` | produto | produto, categoria, faturamento, quantidade, crescimento_pct |
| 4 Previsão | Linha de KPIs | `vw_previsao` + `vw_metricas_modelo` | mês / modelo | ver views |
| 4 | Histórico + ajuste + projeção tracejada | `vw_previsao` | mês | ano_mes, realizado, ajustado, previsto, banda_inf, banda_sup, fase |
| 4 | Tabela modelo vs baseline | `vw_metricas_modelo` | modelo | modelo, mae, mape, r2 |
| todas | Gêmeo tabular (expander de cada gráfico) | a mesma view do gráfico | — | — |
| todas | Filtros da sidebar (opções) | `vw_vendas` (valores distintos de categoria, uf, status; min/max de data) | item | ver view |

## Comportamento dos filtros por view

Quintis, coortes e percentuais acumulados só têm validade calculados sobre a base inteira —
recalcular por recorte mudaria a pergunta respondida. Por isso:

- Respondem a **todos** os filtros (via WHERE no app): `vw_faturamento_mensal`, `vw_vendas`.
- Respondem a **período e categoria**: `vw_crescimento_categoria` - o MoM é pré-calculado com
  janela por categoria, então cortar UF exigiria recalcular a janela no app (proibido);
  filtrar meses ou remover categorias inteiras não altera o cálculo.
- Respondem **só a período**: `vw_kpis_mensais`.
- **Base completa** (status = venda concretizada, sem reagir a filtro de categoria/UF):
  `vw_rfm`, `vw_coorte_retencao`, `vw_curva_retencao`, `vw_pareto_produtos`,
  `vw_produtos_metricas`, `vw_receita_top_clientes`. Cada gráfico desses leva nota curta na UI.

## Views (schema `dw`, uma por arquivo em `sql/views/`)

| View | O que responde | SQL exercitado |
|---|---|---|
| `vw_vendas` | base enriquecida: fato + dims, 1 linha por item | joins do star schema |
| `vw_faturamento_mensal` | quanto faturei por mês/categoria/uf/status | GROUP BY multigrão |
| `vw_kpis_mensais` | os 4 KPIs do enunciado, mês a mês | CTEs, LAG, churn com N |
| `vw_rfm` | segmentação RFM da base | NTILE(5), CASE de segmentos |
| `vw_coorte_retencao` | matriz de retenção por coorte de 1ª compra | CTE de coorte, MIN() OVER |
| `vw_curva_retencao` | curva média de retenção | agregação sobre a coorte |
| `vw_crescimento_categoria` | MoM por categoria | LAG() por partição |
| `vw_produtos_metricas` | crescimento (3m vs 3m anteriores) x volume | janelas com FILTER/CASE |
| `vw_pareto_produtos` | concentração 80/20 do portfólio | SUM() OVER, ROW_NUMBER |
| `vw_receita_top_clientes` | % da receita no top 10% de clientes | NTILE + SUM OVER |
| `vw_previsao` | leitura de `dw.previsao_mensal` | — |
| `vw_metricas_modelo` | leitura de `dw.metricas_modelo` | — |
