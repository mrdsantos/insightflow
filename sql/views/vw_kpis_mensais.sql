-- Os 4 KPIs do enunciado (faturamento, ticket medio, retencao, churn) mes a mes,
-- mais os KPIs de cliente da pagina 2. Base: venda concretizada (Entregue/Enviado).
--
-- Definicoes fixadas na EDA (notebook 02, docs/decisoes.md):
--   retencao(M) = clientes ativos em M que tambem compraram em M-1 / ativos em M-1
--   churn N=90: cliente ativo = comprou nos ultimos 90 dias; churn(M) = clientes que
--   estavam ativos no fim de M-1 e deixaram de estar no fim de M / ativos no fim de M-1
CREATE OR REPLACE VIEW dw.vw_kpis_mensais AS
WITH vendas AS (
    SELECT id_cliente, id_pedido, data_venda, valor_total,
           date_trunc('month', data_venda)::date AS mes_ref
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
),
meses AS (
    SELECT DISTINCT date_trunc('month', data)::date AS mes_ref, ano_mes
    FROM dw.dim_calendario
    WHERE date_trunc('month', data)::date
          BETWEEN (SELECT MIN(mes_ref) FROM vendas) AND (SELECT MAX(mes_ref) FROM vendas)
),
base_mes AS (
    SELECT mes_ref,
           SUM(valor_total)           AS faturamento,
           COUNT(DISTINCT id_pedido)  AS pedidos,
           COUNT(DISTINCT id_cliente) AS clientes_ativos
    FROM vendas
    GROUP BY mes_ref
),
novos AS (
    SELECT mes_primeira AS mes_ref, COUNT(*) AS clientes_novos
    FROM (SELECT id_cliente, MIN(mes_ref) AS mes_primeira FROM vendas GROUP BY id_cliente) p
    GROUP BY mes_primeira
),
-- retencao: LAG sobre a atividade mensal de cada cliente diz se o mes anterior teve compra
atividade AS (
    SELECT id_cliente, mes_ref,
           LAG(mes_ref) OVER (PARTITION BY id_cliente ORDER BY mes_ref) AS mes_atividade_anterior
    FROM (SELECT DISTINCT id_cliente, mes_ref FROM vendas) t
),
retidos_mes AS (
    SELECT mes_ref,
           COUNT(*) FILTER (
               WHERE mes_atividade_anterior = (mes_ref - INTERVAL '1 month')::date
           ) AS retidos
    FROM atividade
    GROUP BY mes_ref
),
-- churn: ultima compra de cada cliente ate o fim de cada mes -> ativo ou nao na janela de 90d
fim_de_mes AS (
    SELECT mes_ref, ano_mes,
           (mes_ref + INTERVAL '1 month' - INTERVAL '1 day')::date AS ultimo_dia
    FROM meses
),
status_cliente AS (
    SELECT c.id_cliente, m.mes_ref,
           (m.ultimo_dia - MAX(v.data_venda)) <= 90 AS ativo_90d
    FROM (SELECT DISTINCT id_cliente FROM vendas) c
    CROSS JOIN fim_de_mes m
    JOIN vendas v ON v.id_cliente = c.id_cliente AND v.data_venda <= m.ultimo_dia
    GROUP BY c.id_cliente, m.mes_ref, m.ultimo_dia
),
churn_mes AS (
    SELECT s.mes_ref,
           COUNT(*) FILTER (WHERE anterior.ativo_90d)                    AS base_ativos_90d,
           COUNT(*) FILTER (WHERE anterior.ativo_90d AND NOT s.ativo_90d) AS churned
    FROM status_cliente s
    JOIN status_cliente anterior
      ON anterior.id_cliente = s.id_cliente
     AND anterior.mes_ref = (s.mes_ref - INTERVAL '1 month')::date
    GROUP BY s.mes_ref
)
SELECT
    m.ano_mes,
    b.faturamento,
    b.pedidos,
    ROUND(b.faturamento / NULLIF(b.pedidos, 0), 2)          AS ticket_medio,
    b.clientes_ativos,
    COALESCE(n.clientes_novos, 0)                           AS clientes_novos,
    ROUND(b.faturamento / NULLIF(b.clientes_ativos, 0), 2)  AS ticket_medio_cliente,
    ROUND(100.0 * r.retidos
          / NULLIF(LAG(b.clientes_ativos) OVER (ORDER BY m.mes_ref), 0), 1) AS taxa_retencao,
    ROUND(100.0 * c.churned / NULLIF(c.base_ativos_90d, 0), 1)              AS churn_rate
FROM meses m
JOIN base_mes b     ON b.mes_ref = m.mes_ref
LEFT JOIN novos n       ON n.mes_ref = m.mes_ref
LEFT JOIN retidos_mes r ON r.mes_ref = m.mes_ref
LEFT JOIN churn_mes c   ON c.mes_ref = m.mes_ref
ORDER BY m.ano_mes;
