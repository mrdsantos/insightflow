"""Cria o database insightflow (se nao existir) e aplica sql/ddl/ em ordem.

Idempotente: rodar duas vezes seguidas nao da erro nem duplica nada.
A DATABASE_URL vem do .env; para criar o database o script conecta ao 'postgres'
trocando so o dbname via psycopg.conninfo (nunca parse manual da URL).
"""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DDL = RAIZ / "sql" / "ddl"
PASTA_VIEWS = RAIZ / "sql" / "views"


def main():
    load_dotenv(RAIZ / ".env")
    url = os.environ["DATABASE_URL"]
    parametros = conninfo_to_dict(url)
    db_alvo = parametros["dbname"]

    admin = make_conninfo(**{**parametros, "dbname": "postgres"})
    with psycopg.connect(admin, autocommit=True) as conn:
        existe = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (db_alvo,)
        ).fetchone()
        if existe:
            print(f"database {db_alvo} ja existe")
        else:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_alvo)))
            print(f"database {db_alvo} criado")

    with psycopg.connect(url) as conn:
        for arquivo in sorted(PASTA_DDL.glob("*.sql")):
            conn.execute(arquivo.read_text(encoding="utf-8"))
            print(f"aplicado {arquivo.name}")
        # views por ultimo: CREATE OR REPLACE depende das tabelas ja existirem
        for arquivo in sorted(PASTA_VIEWS.glob("*.sql")):
            conn.execute(arquivo.read_text(encoding="utf-8"))
            print(f"aplicado views/{arquivo.name}")
        conn.commit()


if __name__ == "__main__":
    main()
