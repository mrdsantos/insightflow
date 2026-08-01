-- Quanto da receita vem do top 10% de clientes (KPI da pagina Clientes).
-- NTILE(10) sobre a receita por cliente em ordem decrescente: decil 1 = top 10%.
-- Estrutural: base completa de venda concretizada, 1 linha de saida.
CREATE OR REPLACE VIEW dw.vw_receita_top_clientes AS
WITH por_cliente AS (
    SELECT id_cliente, SUM(valor_total) AS receita
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
    GROUP BY id_cliente
),
decis AS (
    SELECT receita, NTILE(10) OVER (ORDER BY receita DESC) AS decil
    FROM por_cliente
)
SELECT
    ROUND(100.0 * SUM(receita) FILTER (WHERE decil = 1) / SUM(receita), 1) AS pct_receita_top10
FROM decis;
