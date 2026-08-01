"""Smoke de renderizacao: cada pagina do app roda ate o fim sem excecao.

Pega chave duplicada, import faltando e slug inexistente em definicoes.ajuda()
sem abrir navegador. Pula por alcancabilidade do banco, nao por ausencia de
DATABASE_URL: o .env pode apontar para um Postgres remoto que nao aceita conexao.
"""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app"
PAGINAS = [
    "Home.py",
    "pages/2_Clientes.py",
    "pages/3_Produtos.py",
    "pages/4_Previsão.py",
    "pages/5_Definições.py",
]


def _banco_ok() -> bool:
    load_dotenv()  # replica o que app/dados.py faz no import
    url = os.environ.get("DATABASE_URL")
    if not url:
        return False
    try:
        from sqlalchemy import create_engine, text

        eng = create_engine(
            url.replace("postgresql://", "postgresql+psycopg://", 1),
            connect_args={"connect_timeout": 3},
        )
        with eng.connect() as c:
            c.execute(text("select 1 from dw.vw_kpis_mensais limit 1"))
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _banco_ok(), reason="sem banco alcancavel; o smoke das paginas exige dw populado"
)


@pytest.mark.parametrize("pagina", PAGINAS)
def test_pagina_renderiza_sem_excecao(pagina):
    sys.path.insert(0, str(APP))  # as paginas usam import plano: dados, filtros, theme, ui
    at = AppTest.from_file(str(APP / pagina), default_timeout=60).run()
    assert not at.exception
