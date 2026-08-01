-- Concentracao 80/20 do portfolio (venda concretizada), 1 linha por produto.
-- pct_faturamento e pct_acumulado saem na MESMA escala 0-100 justamente para o
-- grafico de Pareto nao precisar de eixo duplo (proibido no dashboard).
-- Estrutural: base completa, nao reage aos filtros.
CREATE OR REPLACE VIEW dw.vw_pareto_produtos AS
WITH por_produto AS (
    SELECT nome_produto AS produto, SUM(valor_total) AS faturamento
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
    GROUP BY nome_produto
)
SELECT
    produto,
    faturamento,
    ROUND(100.0 * faturamento / SUM(faturamento) OVER (), 2) AS pct_faturamento,
    ROUND(100.0 * SUM(faturamento) OVER (ORDER BY faturamento DESC, produto)
          / SUM(faturamento) OVER (), 2)                     AS pct_acumulado,
    ROW_NUMBER() OVER (ORDER BY faturamento DESC, produto)   AS posicao
FROM por_produto
ORDER BY posicao;
