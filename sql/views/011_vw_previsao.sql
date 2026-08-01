-- Leitura 1:1 da tabela materializada pelo src/modelo/treinar.py.
-- Mesmo sendo passthrough, o dashboard so enxerga views - a tabela pode mudar de
-- forma sem quebrar contrato de tela.
CREATE OR REPLACE VIEW dw.vw_previsao AS
SELECT ano_mes, realizado, ajustado, previsto, banda_inf, banda_sup, fase
FROM dw.previsao_mensal;
