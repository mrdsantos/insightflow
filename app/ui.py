"""Pecas de interface compartilhadas pelas paginas.

Formatacao pt-BR e o gemeo tabular obrigatorio de cada grafico (tooltip nunca
pode ser o unico jeito de ler um valor).
"""

import pandas as pd
import streamlit as st


def fmt_num(v: float, decimais: int = 0) -> str:
    s = f"{v:,.{decimais}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_moeda(v: float, decimais: int = 0) -> str:
    return f"R$ {fmt_num(v, decimais)}"


def fmt_pct(v: float, decimais: int = 1) -> str:
    return f"{fmt_num(v, decimais)}%"


def fmt_compacto(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"R$ {fmt_num(v / 1_000_000, 2)} mi"
    if abs(v) >= 1_000:
        return f"R$ {fmt_num(v / 1_000, 0)} mil"
    return fmt_moeda(v)


def gemeo_tabular(df: pd.DataFrame, rotulo: str = "Ver dados") -> None:
    with st.expander(rotulo):
        st.dataframe(df, width="stretch", hide_index=True)


def nota_estrutural() -> None:
    st.caption(
        "Analise estrutural sobre a base completa de vendas concretizadas; "
        "nao reage aos filtros da barra lateral."
    )
