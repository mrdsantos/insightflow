-- Base enriquecida: fato + dimensoes, 1 linha por item vendido.
-- Alimenta os filtros da sidebar (distintos de categoria/uf/status, min/max de data),
-- os KPIs de produto e serve de gemeo tabular onde o grafico usa esta view.
CREATE OR REPLACE VIEW dw.vw_vendas AS
SELECT
    f.sk_venda,
    f.id_transacao,
    f.id_pedido,
    f.data_venda,
    c.ano_mes,
    c.ano,
    c.mes,
    cl.id_cliente,
    p.nome_produto,
    p.categoria,
    l.cidade,
    l.uf,
    l.pais,
    f.quantidade,
    f.valor_unitario,
    f.valor_total,
    f.metodo_pagamento,
    f.status_pedido
FROM dw.fato_vendas f
JOIN dw.dim_calendario c  ON c.data          = f.data_venda
JOIN dw.dim_cliente    cl ON cl.sk_cliente   = f.sk_cliente
JOIN dw.dim_produto    p  ON p.sk_produto    = f.sk_produto
JOIN dw.dim_localidade l  ON l.sk_localidade = f.sk_localidade;
