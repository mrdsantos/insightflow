-- Crescimento YoY do faturamento mensal com LAG(12) - completa o requisito MoM/YoY.
-- Consumida pelo notebook 02; o MoM por categoria vive em dw.vw_crescimento_categoria.
WITH mensal AS (
    SELECT ano_mes, SUM(valor_total) AS faturamento
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
    GROUP BY ano_mes
)
SELECT
    ano_mes,
    faturamento,
    LAG(faturamento, 12) OVER (ORDER BY ano_mes) AS faturamento_ano_anterior,
    ROUND(
        100.0 * (faturamento - LAG(faturamento, 12) OVER (ORDER BY ano_mes))
        / NULLIF(LAG(faturamento, 12) OVER (ORDER BY ano_mes), 0), 1
    ) AS yoy_pct
FROM mensal
ORDER BY ano_mes;
