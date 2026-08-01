-- Matriz de retencao por coorte de primeira compra (venda concretizada).
-- Linha = mes da primeira compra do cliente; coluna = meses desde a primeira compra;
-- valor = % da coorte que voltou a comprar naquele mes. Estrutural: ignora filtros.
CREATE OR REPLACE VIEW dw.vw_coorte_retencao AS
WITH atividade AS (
    SELECT DISTINCT id_cliente, date_trunc('month', data_venda)::date AS mes
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
),
com_coorte AS (
    SELECT id_cliente, mes,
           MIN(mes) OVER (PARTITION BY id_cliente) AS coorte_data
    FROM atividade
),
tamanho AS (
    SELECT coorte_data, COUNT(DISTINCT id_cliente) AS clientes_coorte
    FROM com_coorte
    GROUP BY coorte_data
),
retidos AS (
    SELECT coorte_data,
           (EXTRACT(YEAR FROM mes) - EXTRACT(YEAR FROM coorte_data))::int * 12
           + (EXTRACT(MONTH FROM mes) - EXTRACT(MONTH FROM coorte_data))::int AS meses_desde,
           COUNT(DISTINCT id_cliente) AS clientes_retidos
    FROM com_coorte
    GROUP BY 1, 2
)
SELECT
    to_char(r.coorte_data, 'YYYY-MM') AS coorte_mes,
    r.meses_desde,
    t.clientes_coorte,
    r.clientes_retidos,
    ROUND(100.0 * r.clientes_retidos / t.clientes_coorte, 1) AS pct_retido
FROM retidos r
JOIN tamanho t USING (coorte_data)
ORDER BY coorte_mes, meses_desde;
