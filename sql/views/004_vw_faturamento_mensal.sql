-- Faturamento por mes x categoria x uf x status, no grao que a sidebar filtra.
-- O app aplica WHERE nos quatro eixos e agrega o que precisar (serie mensal,
-- sazonalidade ano a ano, barras por categoria) sem recalcular logica.
CREATE OR REPLACE VIEW dw.vw_faturamento_mensal AS
SELECT
    c.ano_mes,
    c.ano,
    c.mes,
    p.categoria,
    l.uf,
    f.status_pedido AS status,
    SUM(f.valor_total) AS faturamento,
    SUM(f.quantidade)  AS itens
FROM dw.fato_vendas f
JOIN dw.dim_calendario c ON c.data          = f.data_venda
JOIN dw.dim_produto    p ON p.sk_produto    = f.sk_produto
JOIN dw.dim_localidade l ON l.sk_localidade = f.sk_localidade
GROUP BY c.ano_mes, c.ano, c.mes, p.categoria, l.uf, f.status_pedido;
