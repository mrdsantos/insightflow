-- staging: espelho fiel do CSV, tudo TEXT (a sujeira entra como esta)
CREATE TABLE IF NOT EXISTS staging.vendas_raw (
  id_transacao TEXT, id_pedido TEXT, data_venda TEXT, id_cliente TEXT,
  nome_produto TEXT, categoria_produto TEXT, valor_unitario TEXT, quantidade TEXT,
  localidade_venda TEXT, metodo_pagamento TEXT, status_pedido TEXT,
  carregado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dw.dim_cliente (
  sk_cliente     SERIAL PRIMARY KEY,
  id_cliente     TEXT NOT NULL UNIQUE          -- chave natural do CSV
);

CREATE TABLE IF NOT EXISTS dw.dim_produto (
  sk_produto     SERIAL PRIMARY KEY,
  nome_produto   TEXT NOT NULL,
  categoria      TEXT NOT NULL,                -- normalizada (caixa/acento)
  UNIQUE (nome_produto, categoria)
);

CREATE TABLE IF NOT EXISTS dw.dim_localidade (
  sk_localidade  SERIAL PRIMARY KEY,
  cidade         TEXT NOT NULL,
  uf             TEXT NOT NULL,
  pais           TEXT NOT NULL,
  UNIQUE (cidade, uf, pais)
);

CREATE TABLE IF NOT EXISTS dw.dim_calendario (
  data           DATE PRIMARY KEY,             -- populada jul/2024 -> dez/2026 (folga p/ previsao)
  ano            INT NOT NULL,
  mes            INT NOT NULL,
  nome_mes       TEXT NOT NULL,
  trimestre      INT NOT NULL,
  ano_mes        TEXT NOT NULL                 -- 'YYYY-MM', chave de agregacao mensal
);
