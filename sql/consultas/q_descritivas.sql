-- Estatisticas descritivas por metrica do fato (vendas concretizadas).
-- Consumida pelo notebook 02_eda; nao vira view porque e leitura pontual de EDA.
WITH base AS (
    SELECT valor_unitario, quantidade, valor_total
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
),
pedido AS (
    -- ticket por pedido: soma dos itens do mesmo id_pedido
    SELECT SUM(valor_total) AS valor_pedido
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
    GROUP BY id_pedido
)
SELECT 'valor_unitario' AS metrica,
       MIN(valor_unitario)                                            AS minimo,
       PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY valor_unitario)   AS q1,
       PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY valor_unitario)   AS mediana,
       AVG(valor_unitario)                                            AS media,
       PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY valor_unitario)   AS q3,
       MAX(valor_unitario)                                            AS maximo,
       STDDEV_SAMP(valor_unitario)                                    AS desvio
FROM base
UNION ALL
SELECT 'quantidade',
       MIN(quantidade),
       PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY quantidade),
       PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY quantidade),
       AVG(quantidade),
       PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY quantidade),
       MAX(quantidade),
       STDDEV_SAMP(quantidade)
FROM base
UNION ALL
SELECT 'valor_total_item',
       MIN(valor_total),
       PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY valor_total),
       PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY valor_total),
       AVG(valor_total),
       PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY valor_total),
       MAX(valor_total),
       STDDEV_SAMP(valor_total)
FROM base
UNION ALL
SELECT 'valor_pedido',
       MIN(valor_pedido),
       PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY valor_pedido),
       PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY valor_pedido),
       AVG(valor_pedido),
       PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY valor_pedido),
       MAX(valor_pedido),
       STDDEV_SAMP(valor_pedido)
FROM pedido;
