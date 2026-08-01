-- Curva media de retencao sobre a matriz de coorte.
-- Media ponderada: soma dos retidos / soma dos tamanhos das coortes elegiveis.
-- A grade gerada preenche com zero os meses em que a coorte nao teve ninguem ativo -
-- sem isso a media so veria celulas com retencao > 0 e sairia inflada. So entram
-- pares (coorte, meses_desde) observaveis dentro da janela dos dados.
CREATE OR REPLACE VIEW dw.vw_curva_retencao AS
WITH mes_max AS (
    SELECT date_trunc('month', MAX(data_venda))::date AS m
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
),
coortes AS (
    SELECT DISTINCT
        to_date(coorte_mes || '-01', 'YYYY-MM-DD') AS coorte_data,
        clientes_coorte
    FROM dw.vw_coorte_retencao
),
grade AS (
    SELECT c.coorte_data, c.clientes_coorte, gs.meses_desde
    FROM coortes c
    CROSS JOIN mes_max
    CROSS JOIN LATERAL generate_series(
        0,
        (EXTRACT(YEAR FROM mes_max.m) - EXTRACT(YEAR FROM c.coorte_data))::int * 12
        + (EXTRACT(MONTH FROM mes_max.m) - EXTRACT(MONTH FROM c.coorte_data))::int
    ) AS gs(meses_desde)
)
SELECT
    g.meses_desde,
    ROUND(100.0 * SUM(COALESCE(r.clientes_retidos, 0)) / SUM(g.clientes_coorte), 1) AS pct_medio
FROM grade g
LEFT JOIN dw.vw_coorte_retencao r
       ON to_date(r.coorte_mes || '-01', 'YYYY-MM-DD') = g.coorte_data
      AND r.meses_desde = g.meses_desde
GROUP BY g.meses_desde
ORDER BY g.meses_desde;
