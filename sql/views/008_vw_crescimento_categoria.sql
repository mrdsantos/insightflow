-- Faturamento mensal e crescimento MoM por categoria (venda concretizada).
-- O mom_pct e pre-calculado com LAG por particao, entao esta view so aceita filtro
-- de periodo e de categoria no app: cortar UF exigiria recalcular a janela sobre a
-- base filtrada, e logica analitica nao roda no dashboard. Registrado em decisoes.md.
-- LAG pega o mes anterior existente na serie; mes sem venda na categoria criaria um
-- MoM contra o penultimo mes, mas com este volume nao ha buraco mensal por categoria.
CREATE OR REPLACE VIEW dw.vw_crescimento_categoria AS
WITH mensal AS (
    SELECT ano_mes, categoria, SUM(valor_total) AS faturamento
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
    GROUP BY ano_mes, categoria
)
SELECT
    ano_mes,
    categoria,
    faturamento,
    ROUND(
        100.0 * (faturamento - LAG(faturamento) OVER (PARTITION BY categoria ORDER BY ano_mes))
        / NULLIF(LAG(faturamento) OVER (PARTITION BY categoria ORDER BY ano_mes), 0), 1
    ) AS mom_pct
FROM mensal
ORDER BY categoria, ano_mes;
