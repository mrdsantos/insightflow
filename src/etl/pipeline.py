"""Pipeline completo: CSV -> staging -> validacao -> dw. Uso: python -m src.etl.pipeline

Full refresh idempotente: rodar duas vezes deixa as contagens identicas.
"""

import logging
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from src.etl import carga, validacao

RAIZ = Path(__file__).resolve().parent.parent.parent
CAMINHO_CSV = RAIZ / "dados" / "ecom_data.csv"

log = logging.getLogger("etl")


def executa(url=None):
    load_dotenv(RAIZ / ".env")
    url = url or os.environ["DATABASE_URL"]

    with psycopg.connect(url) as conn:
        n_staging = carga.carrega_staging(conn, CAMINHO_CSV)
        log.info("extract: %s linhas do csv para o staging", n_staging)

        linhas = carga.le_staging(conn)
        limpos, rejeitados, n_duplicatas = validacao.valida_e_limpa(linhas)
        log.info("transform: %s validas, %s rejeitadas, %s duplicatas descartadas",
                 len(limpos), len(rejeitados), n_duplicatas)

        n_calendario = carga.garante_calendario(conn)
        if n_calendario:
            log.info("load: dim_calendario populada com %s dias", n_calendario)
        dims = carga.carrega_dimensoes(conn, limpos)
        log.info("load: dims recarregadas %s", dims)
        n_fato = carga.carrega_fato(conn, limpos)
        n_quarentena = carga.carrega_quarentena(conn, rejeitados)
        log.info("load: %s linhas no fato, %s na quarentena", n_fato, n_quarentena)

    return {
        "staging": n_staging,
        "validas": len(limpos),
        "rejeitadas": len(rejeitados),
        "duplicatas": n_duplicatas,
        "fato": n_fato,
        "quarentena": n_quarentena,
        "dims": dims,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    executa()
