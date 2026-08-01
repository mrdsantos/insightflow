# Contrato de dados

Tabela que liga cada elemento de tela do dashboard a view SQL que o alimenta. Regras que ela
impoe: nenhuma view fora desta tabela sera construida (view orfa) e nenhum elemento de tela
fica sem fonte. O app so aplica filtro (WHERE) e agregacao trivial (soma, contagem, pivot);
toda logica analitica (janelas, quintis, percentuais acumulados, definicao de churn) vive nas
views versionadas em `sql/views/`.

| Pagina | Elemento | View / query | Granularidade | Colunas retornadas |
|---|---|---|---|---|
| 1 Visao Geral | Linha de 4 KPIs + deltas + sparklines | `vw_kpis_mensais` | mes | ano_mes, faturamento, pedidos, ticket_medio, clientes_ativos, clientes_novos, ticket_medio_cliente, taxa_retencao, churn_rate |
| 1 | Serie temporal de faturamento | `vw_faturamento_mensal` | mes x categoria x uf x status | ano_mes, categoria, uf, status, faturamento, itens |
| 1 | Sazonalidade ano a ano | `vw_faturamento_mensal` (app separa por ano) | idem | idem |
| 1 | Barras por categoria (cor unica) | `vw_faturamento_mensal` (app agrega) | idem | idem |
| 2 Clientes | Linha de KPIs | `vw_kpis_mensais` + `vw_receita_top_clientes` | mes / 1 linha | (acima) / pct_receita_top10 |
| 2 | Heatmap RFM (R x F) | `vw_rfm` (app pivota contagem) | cliente | id_cliente, recencia_dias, frequencia, monetario, score_r, score_f, score_m, segmento |
| 2 | Barras tamanho/receita por segmento | `vw_rfm` (app agrega) | cliente | idem |
| 2 | Dispersao Recencia x Monetario (emphasis 3) | `vw_rfm` | cliente | idem |
| 2 | Matriz de coorte | `vw_coorte_retencao` | coorte x meses_desde | coorte_mes, meses_desde, clientes_coorte, clientes_retidos, pct_retido |
| 2 | Curva de retencao media | `vw_curva_retencao` | meses_desde | meses_desde, pct_medio |
| 3 Produtos | Linha de KPIs | `vw_vendas` (SKUs ativos, categoria lider via agregacao trivial) + `vw_pareto_produtos` (produto lider, concentracao) | item / produto | ver views |
| 3 | Pareto (% na mesma escala, sem eixo duplo) | `vw_pareto_produtos` | produto | produto, faturamento, pct_faturamento, pct_acumulado, posicao |
| 3 | Small multiples MoM por categoria | `vw_crescimento_categoria` | mes x categoria | ano_mes, categoria, faturamento, mom_pct |
| 3 | Matriz crescimento x faturamento (emphasis 3) | `vw_produtos_metricas` | produto | produto, categoria, faturamento, quantidade, crescimento_pct |
| 4 Previsao | Linha de KPIs | `vw_previsao` + `vw_metricas_modelo` | mes / modelo | ver views |
| 4 | Historico + ajuste + projecao tracejada | `vw_previsao` | mes | ano_mes, realizado, ajustado, previsto, banda_inf, banda_sup, fase |
| 4 | Tabela modelo vs baseline | `vw_metricas_modelo` | modelo | modelo, mae, mape, r2 |
| todas | Gemeo tabular (expander de cada grafico) | a mesma view do grafico | — | — |
| todas | Filtros da sidebar (opcoes) | `vw_vendas` (valores distintos de categoria, uf, status; min/max de data) | item | ver view |

## Comportamento dos filtros por view

Quintis, coortes e percentuais acumulados so tem validade calculados sobre a base inteira —
recalcular por recorte mudaria a pergunta respondida. Por isso:

- Respondem a **todos** os filtros (via WHERE no app): `vw_faturamento_mensal`, `vw_vendas`.
- Respondem a **periodo e categoria**: `vw_crescimento_categoria` - o MoM e pre-calculado com
  janela por categoria, entao cortar UF exigiria recalcular a janela no app (proibido);
  filtrar meses ou remover categorias inteiras nao altera o calculo.
- Respondem **so a periodo**: `vw_kpis_mensais`.
- **Base completa** (status = venda concretizada, sem reagir a filtro de categoria/UF):
  `vw_rfm`, `vw_coorte_retencao`, `vw_curva_retencao`, `vw_pareto_produtos`,
  `vw_produtos_metricas`, `vw_receita_top_clientes`. Cada grafico desses leva nota curta na UI.

## Views (schema `dw`, uma por arquivo em `sql/views/`)

| View | O que responde | SQL exercitado |
|---|---|---|
| `vw_vendas` | base enriquecida: fato + dims, 1 linha por item | joins do star schema |
| `vw_faturamento_mensal` | quanto faturei por mes/categoria/uf/status | GROUP BY multi-grao |
| `vw_kpis_mensais` | os 4 KPIs do enunciado, mes a mes | CTEs, LAG, churn com N |
| `vw_rfm` | segmentacao RFM da base | NTILE(5), CASE de segmentos |
| `vw_coorte_retencao` | matriz de retencao por coorte de 1a compra | CTE de coorte, MIN() OVER |
| `vw_curva_retencao` | curva media de retencao | agregacao sobre a coorte |
| `vw_crescimento_categoria` | MoM por categoria | LAG() por particao |
| `vw_produtos_metricas` | crescimento (3m vs 3m anteriores) x volume | janelas com FILTER/CASE |
| `vw_pareto_produtos` | concentracao 80/20 do portfolio | SUM() OVER, ROW_NUMBER |
| `vw_receita_top_clientes` | % da receita no top 10% de clientes | NTILE + SUM OVER |
| `vw_previsao` | leitura de `dw.previsao_mensal` | — |
| `vw_metricas_modelo` | leitura de `dw.metricas_modelo` | — |
