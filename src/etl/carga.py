"""Cargas no PostgreSQL: CSV -> staging (extract) e staging limpo -> dw.

Full refresh: staging e dw (exceto dim_calendario) sao truncados e recarregados
a cada execucao. Com seed fixa e 8k linhas, isso e deterministico e simples de
auditar - rodar de novo apontando para o VPS reproduz tudo.
"""

import csv
import json
from datetime import date, timedelta

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


NOMES_MES = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def garante_calendario(conn, inicio=date(2024, 7, 1), fim=date(2026, 12, 31)):
    """Popula dw.dim_calendario uma unica vez (folga ate dez/2026 para a previsao)."""
    with conn.cursor() as cur:
        if cur.execute("SELECT count(*) FROM dw.dim_calendario").fetchone()[0] > 0:
            return 0
        dias = []
        d = inicio
        while d <= fim:
            dias.append((d, d.year, d.month, NOMES_MES[d.month - 1],
                         (d.month - 1) // 3 + 1, f"{d.year:04d}-{d.month:02d}"))
            d += timedelta(days=1)
        cur.executemany(
            "INSERT INTO dw.dim_calendario (data, ano, mes, nome_mes, trimestre, ano_mes) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            dias,
        )
    conn.commit()
    return len(dias)


def carrega_dimensoes(conn, registros):
    """Full refresh das dims (menos calendario) a partir dos registros limpos."""
    clientes = sorted({r["id_cliente"] for r in registros})
    produtos = sorted({(r["nome_produto"], r["categoria"]) for r in registros})
    localidades = sorted({(r["cidade"], r["uf"], r["pais"]) for r in registros})

    with conn.cursor() as cur:
        cur.execute(
            "TRUNCATE dw.fato_vendas, dw.dim_cliente, dw.dim_produto, dw.dim_localidade "
            "RESTART IDENTITY"
        )
        cur.executemany(
            "INSERT INTO dw.dim_cliente (id_cliente) VALUES (%s) ON CONFLICT DO NOTHING",
            [(c,) for c in clientes],
        )
        cur.executemany(
            "INSERT INTO dw.dim_produto (nome_produto, categoria) VALUES (%s, %s) "
            "ON CONFLICT DO NOTHING",
            produtos,
        )
        cur.executemany(
            "INSERT INTO dw.dim_localidade (cidade, uf, pais) VALUES (%s, %s, %s) "
            "ON CONFLICT DO NOTHING",
            localidades,
        )
    conn.commit()
    return {"clientes": len(clientes), "produtos": len(produtos), "localidades": len(localidades)}


def carrega_fato(conn, registros):
    """Insere o fato resolvendo as SKs por lookup nas dims recem-carregadas."""
    with conn.cursor() as cur:
        sk_cliente = dict(cur.execute("SELECT id_cliente, sk_cliente FROM dw.dim_cliente").fetchall())
        sk_produto = {(n, c): sk for n, c, sk in
                      cur.execute("SELECT nome_produto, categoria, sk_produto FROM dw.dim_produto").fetchall()}
        sk_localidade = {(c, u, p): sk for c, u, p, sk in
                         cur.execute("SELECT cidade, uf, pais, sk_localidade FROM dw.dim_localidade").fetchall()}

        cur.executemany(
            "INSERT INTO dw.fato_vendas (id_transacao, id_pedido, data_venda, sk_cliente, "
            "sk_produto, sk_localidade, quantidade, valor_unitario, metodo_pagamento, status_pedido) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [(r["id_transacao"], r["id_pedido"], r["data_venda"],
              sk_cliente[r["id_cliente"]],
              sk_produto[(r["nome_produto"], r["categoria"])],
              sk_localidade[(r["cidade"], r["uf"], r["pais"])],
              r["quantidade"], r["valor_unitario"], r["metodo_pagamento"], r["status_pedido"])
             for r in registros],
        )
    conn.commit()
    return len(registros)
