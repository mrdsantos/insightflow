"""Conexao com o banco e leitura das views.

O dashboard nunca roda logica analitica propria: toda janela, quintil e percentual
acumulado vive nas views de dw. Aqui so existe leitura com cache; filtro e agregacao
trivial ficam em filtros.py e nas paginas.
"""

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


@st.cache_resource
def _engine():
    # URL inteira do .env; so o esquema muda porque o driver instalado e o psycopg 3
    # e o SQLAlchemy tentaria importar psycopg2 com o esquema postgresql:// puro.
    url = os.environ["DATABASE_URL"]
    return create_engine(url.replace("postgresql://", "postgresql+psycopg://", 1))


@st.cache_data(ttl=600)
def ler_view(nome: str) -> pd.DataFrame:
    return pd.read_sql(f"SELECT * FROM dw.{nome}", _engine())
