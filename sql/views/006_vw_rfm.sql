-- Segmentacao RFM da base completa (venda concretizada), 1 linha por cliente.
-- Estrutural: nao reage aos filtros do dashboard - quintil so vale sobre a base inteira.
-- Data de referencia = ultima venda da base (snapshot), nao now(): dataset sintetico
-- congelado em jun/2026 deixaria todo mundo "antigo" se a referencia fosse o relogio.
--
-- NTILE(5) reparte empates arbitrariamente (muitos clientes com frequencia 1);
-- aceitavel porque o quintil e ranking relativo, nao faixa de negocio.
CREATE OR REPLACE VIEW dw.vw_rfm AS
WITH base AS (
    SELECT id_cliente, id_pedido, data_venda, valor_total
    FROM dw.vw_vendas
    WHERE status_pedido IN ('Entregue', 'Enviado')
),
clientes AS (
    SELECT
        id_cliente,
        (SELECT MAX(data_venda) FROM base) - MAX(data_venda) AS recencia_dias,
        COUNT(DISTINCT id_pedido)                            AS frequencia,
        SUM(valor_total)                                     AS monetario
    FROM base
    GROUP BY id_cliente
),
scores AS (
    SELECT
        clientes.*,
        -- recencia: quanto menor, melhor -> DESC poe os mais recentes no quintil 5
        NTILE(5) OVER (ORDER BY recencia_dias DESC) AS score_r,
        NTILE(5) OVER (ORDER BY frequencia)         AS score_f,
        NTILE(5) OVER (ORDER BY monetario)          AS score_m
    FROM clientes
)
SELECT
    id_cliente,
    recencia_dias,
    frequencia,
    monetario,
    score_r,
    score_f,
    score_m,
    -- grade R x F, primeira condicao que casa vence; particao completa dos 25 pares
    CASE
        WHEN score_r >= 4 AND score_f >= 4 THEN 'Campeões'
        WHEN score_r >= 4 AND score_f >= 2 THEN 'Potenciais leais'
        WHEN score_r >= 4                  THEN 'Novos'
        WHEN score_r = 3  AND score_f >= 4 THEN 'Leais'
        WHEN score_r = 3  AND score_f >= 2 THEN 'Precisam de atenção'
        WHEN score_r = 3                   THEN 'Promissores'
        WHEN score_f >= 4                  THEN 'Não pode perder'
        WHEN score_f >= 2                  THEN 'Em Risco'
        WHEN score_r = 2                   THEN 'Prestes a dormir'
        ELSE 'Perdidos'
    END AS segmento
FROM scores;
