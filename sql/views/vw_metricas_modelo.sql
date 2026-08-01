-- Leitura 1:1 de dw.metricas_modelo (materializada pelo src/modelo/treinar.py).
CREATE OR REPLACE VIEW dw.vw_metricas_modelo AS
SELECT modelo, mae, mape, r2
FROM dw.metricas_modelo;
