"""Pecas de interface compartilhadas pelas paginas.

Formatacao pt-BR e o gemeo tabular obrigatorio de cada grafico (tooltip nunca
pode ser o unico jeito de ler um valor).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import theme

# A modebar do Plotly e fixa em ingles no bundle. Sai sem perda: todo grafico
# tem gemeo tabular, que e o caminho oficial para ler o valor.
CONFIG_GRAFICO = {"displayModeBar": False}

MESES = ["jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]


def rotulo_mes(ano_mes: str) -> str:
    """'2026-07' -> 'jul/2026'."""
    return f"{MESES[int(ano_mes[5:]) - 1]}/{ano_mes[:4]}"


def eixo_mes(ano_mes, passo: int = 1, como_data: bool = False) -> dict:
    """Ticks de mes em pt-BR, para `fig.update_xaxes(**ui.eixo_mes(...))`.

    Sem isso o Plotly rotula eixo de data no locale dele e sai "Jan 2026".
    Com como_data=True os tickvals saem como Timestamp, para o eixo continuar
    sendo datetime - a previsao depende disso por causa das linhas de fase.
    """
    meses = sorted(set(ano_mes))[::passo]
    return dict(
        tickmode="array",
        tickvals=[pd.Timestamp(m + "-01") for m in meses] if como_data else meses,
        ticktext=[rotulo_mes(m) for m in meses],
    )


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


def stat_tile(
    col,
    titulo: str,
    valor: str,
    serie: pd.Series | None = None,
    delta_texto: str | None = None,
    subiu: bool = True,
    bom: bool = True,
    key: str | None = None,
) -> None:
    """Stat tile: valor grande, delta com seta e cor de status, sparkline.

    Para um numero unico, o numero e o grafico - por isso tile e nao barra.
    As cores de status valem so para o delta, nunca para series.
    """
    with col.container(border=True):
        st.caption(titulo)
        st.markdown(
            f"<div style='font-size:1.7rem;font-weight:600;line-height:1.15;"
            f"color:{theme.TINTA}'>{valor}</div>",
            unsafe_allow_html=True,
        )
        if delta_texto is not None:
            cor = theme.STATUS_BOM if bom else theme.STATUS_CRITICO
            seta = "&#8593;" if subiu else "&#8595;"
            st.markdown(
                f"<span style='color:{cor};font-size:0.9rem'>{seta} {delta_texto}"
                f"</span> <span style='color:{theme.ROTULO_EIXO};font-size:0.8rem'>"
                f"vs periodo anterior</span>",
                unsafe_allow_html=True,
            )
        if serie is not None and len(serie) > 1:
            fig = go.Figure(
                go.Scatter(
                    y=serie, mode="lines",
                    line=dict(color=theme.AZUL, width=2), hoverinfo="skip",
                )
            )
            fig.update_layout(
                height=48, margin=dict(l=0, r=0, t=2, b=2), showlegend=False,
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                paper_bgcolor=theme.TRANSPARENTE, plot_bgcolor=theme.TRANSPARENTE,
            )
            st.plotly_chart(
                fig, width="stretch", key=key,
                config={"displayModeBar": False, "staticPlot": True},
            )


def gemeo_tabular(df: pd.DataFrame, rotulo: str = "Ver dados") -> None:
    with st.expander(rotulo):
        st.dataframe(df, width="stretch", hide_index=True)


def nota_estrutural() -> None:
    st.caption(
        "Analise estrutural sobre a base completa de vendas concretizadas; "
        "nao reage aos filtros da barra lateral."
    )
