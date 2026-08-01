-- materializadas pelo src/modelo/treinar.py (bloco 4); o dashboard le views sobre elas
CREATE TABLE IF NOT EXISTS dw.previsao_mensal (
  ano_mes    TEXT PRIMARY KEY,
  realizado  NUMERIC(14,2),
  ajustado   NUMERIC(14,2),                    -- fitted no periodo de teste
  previsto   NUMERIC(14,2),
  banda_inf  NUMERIC(14,2),
  banda_sup  NUMERIC(14,2),
  fase       TEXT NOT NULL                     -- 'treino' | 'teste' | 'futuro'
);

CREATE TABLE IF NOT EXISTS dw.metricas_modelo (
  modelo TEXT PRIMARY KEY,                     -- 'media_movel' | 'regressao'
  mae NUMERIC(14,2), mape NUMERIC(8,4), r2 NUMERIC(8,4)
);
