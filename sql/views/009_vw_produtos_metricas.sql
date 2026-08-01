-- Metricas por produto para a matriz crescimento x faturamento da pagina Produtos.
-- crescimento_pct = faturamento dos ultimos 3 meses vs os 3 meses anteriores,
-- ancorado no ultimo mes com venda (dataset congelado; now() deixaria tudo zerado).
-- Estrutural: base completa de venda concretizada, nao reage aos filtros.
CREATE OR REPLACE VIEW dw.vw_produtos_metricas AS
WITH ref AS (
    SELECT date_trunc('month', MAX(data_venda))::date AS mes_max
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
),
base AS (
    SELECT nome_produto, categoria, valor_total, quantidade,
           date_trunc('month', data_venda)::date AS mes
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
)
SELECT
    b.nome_produto AS produto,
    b.categoria,
    SUM(b.valor_total) AS faturamento,
    SUM(b.quantidade)  AS quantidade,
    ROUND(
        100.0 * (
            SUM(b.valor_total) FILTER (WHERE b.mes >= r.mes_max - INTERVAL '2 months')
            - SUM(b.valor_total) FILTER (WHERE b.mes >= r.mes_max - INTERVAL '5 months'
                                           AND b.mes <  r.mes_max - INTERVAL '2 months')
        )
        / NULLIF(SUM(b.valor_total) FILTER (WHERE b.mes >= r.mes_max - INTERVAL '5 months'
                                              AND b.mes <  r.mes_max - INTERVAL '2 months'), 0), 1
    ) AS crescimento_pct
FROM base b
CROSS JOIN ref r
GROUP BY b.nome_produto, b.categoria;
