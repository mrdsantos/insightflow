CREATE TABLE IF NOT EXISTS dw.fato_vendas (
  sk_venda        BIGSERIAL PRIMARY KEY,
  id_transacao    TEXT NOT NULL UNIQUE,        -- garante idempotencia logica
  id_pedido       TEXT NOT NULL,               -- desvio documentado (market basket)
  data_venda      DATE NOT NULL REFERENCES dw.dim_calendario(data),
  sk_cliente      INT  NOT NULL REFERENCES dw.dim_cliente(sk_cliente),
  sk_produto      INT  NOT NULL REFERENCES dw.dim_produto(sk_produto),
  sk_localidade   INT  NOT NULL REFERENCES dw.dim_localidade(sk_localidade),
  quantidade      INT  NOT NULL CHECK (quantidade > 0),
  valor_unitario  NUMERIC(12,2) NOT NULL CHECK (valor_unitario >= 0),
  valor_total     NUMERIC(14,2) GENERATED ALWAYS AS (quantidade * valor_unitario) STORED,
  metodo_pagamento TEXT NOT NULL,              -- dimensao degenerada
  status_pedido    TEXT NOT NULL               -- dimensao degenerada
);
CREATE INDEX IF NOT EXISTS ix_fato_data     ON dw.fato_vendas (data_venda);
CREATE INDEX IF NOT EXISTS ix_fato_cliente  ON dw.fato_vendas (sk_cliente);
CREATE INDEX IF NOT EXISTS ix_fato_produto  ON dw.fato_vendas (sk_produto);
CREATE INDEX IF NOT EXISTS ix_fato_status   ON dw.fato_vendas (status_pedido);
CREATE INDEX IF NOT EXISTS ix_fato_pedido   ON dw.fato_vendas (id_pedido);
