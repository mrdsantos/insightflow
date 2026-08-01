"""Cargas no PostgreSQL: CSV -> staging (extract) e staging limpo -> dw.

Full refresh: staging e dw (exceto dim_calendario) sao truncados e recarregados
a cada execucao. Com seed fixa e 8k linhas, isso e deterministico e simples de
auditar - rodar de novo apontando para o VPS reproduz tudo.
"""

import csv
from pathlib import Path

COLUNAS_STAGING = [
    "id_transacao", "id_pedido", "data_venda", "id_cliente", "nome_produto",
    "categoria_produto", "valor_unitario", "quantidade", "localidade_venda",
    "metodo_pagamento", "status_pedido",
]


def carrega_staging(conn, caminho_csv):
    """Truncate + insert do CSV inteiro em staging.vendas_raw, tudo como texto."""
    with open(caminho_csv, encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        linhas = [
            tuple(r[c] if r[c] != "" else None for c in (
                "ID_Transacao", "ID_Pedido", "Data_Venda", "ID_Cliente", "Nome_Produto",
                "Categoria_Produto", "Valor_Unitario", "Quantidade", "Localidade_Venda",
                "Metodo_Pagamento", "Status_Pedido",
            ))
            for r in leitor
        ]

    with conn.cursor() as cur:
        cur.execute("TRUNCATE staging.vendas_raw")
        cur.executemany(
            f"INSERT INTO staging.vendas_raw ({', '.join(COLUNAS_STAGING)}) "
            f"VALUES ({', '.join(['%s'] * len(COLUNAS_STAGING))})",
            linhas,
        )
    conn.commit()
    return len(linhas)


def carrega_quarentena(conn, rejeitados):
    """Grava cada linha rejeitada inteira (JSONB) com o motivo da rejeicao."""
    import json

    with conn.cursor() as cur:
        cur.execute("TRUNCATE dw.quarentena")
        cur.executemany(
            "INSERT INTO dw.quarentena (registro, motivo, etapa) VALUES (%s, %s, 'validacao')",
            [(json.dumps(linha, ensure_ascii=False), motivo) for linha, motivo in rejeitados],
        )
    conn.commit()
    return len(rejeitados)


def le_staging(conn):
    """Devolve as linhas do staging como lista de dicts de texto (None preservado)."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT {', '.join(COLUNAS_STAGING)} FROM staging.vendas_raw")
        return [dict(zip(COLUNAS_STAGING, linha)) for linha in cur.fetchall()]
