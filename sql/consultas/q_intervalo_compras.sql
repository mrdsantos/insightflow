-- Distribuicao do intervalo (dias) entre compras consecutivas do mesmo cliente.
-- Base da escolha do N de churn: cliente sem comprar ha mais de N dias = churned.
-- Compra = pedido concretizado (Entregue/Enviado); o grao e pedido, nao item.
WITH pedidos AS (
    SELECT DISTINCT id_cliente, id_pedido, data_venda
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
),
intervalos AS (
    SELECT
        id_cliente,
        data_venda - LAG(data_venda) OVER (
            PARTITION BY id_cliente ORDER BY data_venda
        ) AS dias
    FROM pedidos
)
SELECT
    COUNT(*)                                             AS n_intervalos,
    MIN(dias)                                            AS minimo,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY dias)   AS mediana,
    AVG(dias)                                            AS media,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY dias)   AS p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY dias)   AS p90,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY dias)   AS p95,
    MAX(dias)                                            AS maximo
FROM intervalos
WHERE dias IS NOT NULL AND dias > 0;
