"""Pagina 4 - Previsao (esqueleto; o modelo e entrega da sprint 4)."""

import streamlit as st

st.set_page_config(page_title="InsightFlow - Previsao", layout="wide")

import filtros
import ui

st.title("Quanto vou faturar no proximo mes, e o quanto posso confiar nisso?")

op = filtros.opcoes()
filtros.sidebar(op)

st.info(
    "Modelo em construcao. Esta pagina vai mostrar a previsao de faturamento do "
    "proximo mes com baseline de media movel, regressao com tendencia e dummies "
    "de mes, e as metricas MAE, MAPE e R2 comparadas entre os dois."
)

c1, c2, c3, c4 = st.columns(4)
ui.stat_tile(c1, "Previsao do proximo mes", "em breve")
ui.stat_tile(c2, "MAE", "em breve")
ui.stat_tile(c3, "MAPE", "em breve")
ui.stat_tile(c4, "R2", "em breve")
