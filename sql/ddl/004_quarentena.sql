-- todo registro rejeitado na validacao cai aqui, inteiro e com motivo
CREATE TABLE IF NOT EXISTS dw.quarentena (
  id_quarentena  BIGSERIAL PRIMARY KEY,
  registro       JSONB NOT NULL,               -- linha original inteira, como veio
  motivo         TEXT NOT NULL,                -- ex.: 'quantidade negativa', 'data invalida'
  etapa          TEXT NOT NULL,                -- 'validacao' | 'transformacao'
  criado_em      TIMESTAMPTZ NOT NULL DEFAULT now()
);
