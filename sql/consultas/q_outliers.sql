-- Limites de outlier de valor_unitario por categoria: IQR (Tukey, 1.5x) e z-score (3 desvios)
-- lado a lado, com a contagem de pontos que cada criterio marcaria. Consumida pelo
-- notebook 02 para justificar a escolha do criterio - a decisao final vai em decisoes.md.
WITH base AS (
    SELECT categoria, valor_unitario
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
),
resumo AS (
    SELECT categoria,
           COUNT(*)                                                     AS n,
           PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY valor_unitario) AS q1,
           PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY valor_unitario) AS q3,
           AVG(valor_unitario)                                          AS media,
           STDDEV_SAMP(valor_unitario)                                  AS desvio
    FROM base
    GROUP BY categoria
)
SELECT
    r.categoria,
    r.n,
    ROUND(r.q1::numeric, 2)                                AS q1,
    ROUND(r.q3::numeric, 2)                                AS q3,
    ROUND((r.q3 + 1.5 * (r.q3 - r.q1))::numeric, 2)        AS limite_iqr,
    ROUND((r.media + 3 * r.desvio)::numeric, 2)            AS limite_z3,
    COUNT(*) FILTER (WHERE b.valor_unitario > r.q3 + 1.5 * (r.q3 - r.q1)) AS outliers_iqr,
    COUNT(*) FILTER (WHERE b.valor_unitario > r.media + 3 * r.desvio)     AS outliers_z3
FROM resumo r
JOIN base b USING (categoria)
GROUP BY r.categoria, r.n, r.q1, r.q3, r.media, r.desvio
ORDER BY r.categoria;
