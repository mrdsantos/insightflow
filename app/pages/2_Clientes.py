"""Pagina 2 - Clientes."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="InsightFlow - Clientes", layout="wide")

import dados
import filtros
import theme
import ui

st.title("Quem são meus clientes e quais estão em risco?")

op = filtros.opcoes()
sel = filtros.sidebar(op)

kpis_per = filtros.aplicar(dados.ler_view("vw_kpis_mensais"), sel, quais=("periodo",))
rfm = dados.ler_view("vw_rfm")
coorte = dados.ler_view("vw_coorte_retencao")
curva = dados.ler_view("vw_curva_retencao")
top10 = dados.ler_view("vw_receita_top_clientes")

if kpis_per.empty:
    st.warning("Nenhum dado no recorte selecionado. Ajuste os filtros.")
    st.stop()

RAMPA = [[i / (len(theme.RAMPA_AZUL) - 1), cor] for i, cor in enumerate(theme.RAMPA_AZUL)]


# ---- KPIs -------------------------------------------------------------------

mensal = kpis_per.sort_values("ano_mes")
c1, c2, c3, c4 = st.columns(4)
ui.stat_tile(
    c1, "Clientes Ativos (média mensal)",
    ui.fmt_num(mensal["clientes_ativos"].mean()),
    serie=mensal["clientes_ativos"], key="spark_ativos",
)
ui.stat_tile(
    c2, "Novos no Período", ui.fmt_num(mensal["clientes_novos"].sum()),
    serie=mensal["clientes_novos"], key="spark_novos",
)
ui.stat_tile(
    c3, "Ticket Médio por Cliente",
    ui.fmt_moeda(mensal["faturamento"].sum() / mensal["clientes_ativos"].sum(), 2),
    serie=mensal["ticket_medio_cliente"], key="spark_ticket_cli",
)
ui.stat_tile(
    c4, "Receita no Top 10% de clientes",
    ui.fmt_pct(top10["pct_receita_top10"].iloc[0]),
)
with c4:
    st.caption("Base completa de vendas concretizadas; não reage aos filtros.")

aba_seg, aba_ret = st.tabs(["Segmentação", "Retenção"])


# ---- Aba Segmentacao --------------------------------------------------------

with aba_seg:
    ui.nota_estrutural()

    col_esq, col_dir = st.columns(2)

    # Matriz RFM: contagem de clientes por celula R x F
    grade = (
        rfm.groupby(["score_f", "score_r"]).size().unstack(fill_value=0)
        .reindex(index=range(1, 6), columns=range(1, 6), fill_value=0)
    )
    fig = go.Figure(
        go.Heatmap(
            z=grade.values,
            x=[str(c) for c in grade.columns],
            y=[str(i) for i in grade.index],
            colorscale=RAMPA,
            colorbar=dict(title="Clientes", outlinewidth=0),
            hovertemplate="R=%{x}, F=%{y}: %{z} clientes<extra></extra>",
        )
    )
    fig.update_layout(
        title="Matriz RFM: clientes por Recência x Frequência",
        xaxis_title="Score de recência (5 = comprou há pouco)",
        yaxis_title="Score de frequência (5 = compra mais)",
        height=420,
    )
    with col_esq:
        st.plotly_chart(fig, width="stretch", key="rfm_heatmap", config=ui.CONFIG_GRAFICO)
        ui.gemeo_tabular(
            grade.reset_index().rename(columns={"score_f": "score_f \\ score_r"})
        )

    # Tamanho e receita por segmento, barras horizontais de cor unica
    seg = (
        rfm.groupby("segmento")
        .agg(clientes=("id_cliente", "count"), receita=("monetario", "sum"))
        .sort_values("clientes")
    )
    fig = go.Figure(
        go.Bar(
            x=seg["clientes"], y=seg.index, orientation="h",
            marker_color=theme.AZUL, showlegend=False,
        )
    )
    fig.update_layout(title="Clientes por segmento RFM", height=420)
    with col_dir:
        st.plotly_chart(fig, width="stretch", key="rfm_segmentos", config=ui.CONFIG_GRAFICO)
        ui.gemeo_tabular(seg.sort_values("clientes", ascending=False).reset_index())

    fig = go.Figure(
        go.Bar(
            x=seg.sort_values("receita")["receita"],
            y=seg.sort_values("receita").index,
            orientation="h", marker_color=theme.AZUL, showlegend=False,
        )
    )
    fig.update_layout(title="Receita por segmento RFM", height=420)
    col_esq2, col_dir2 = st.columns(2)
    with col_esq2:
        st.plotly_chart(fig, width="stretch", key="rfm_receita", config=ui.CONFIG_GRAFICO)
        ui.gemeo_tabular(
            seg.sort_values("receita", ascending=False).reset_index()[
                ["segmento", "receita"]
            ]
        )

    # Dispersao Recencia x Monetario com emphasis: 3 segmentos em cor, resto cinza.
    # Dispersao e forma par-a-par: teto de 3 series coloridas; colorir os 10
    # segmentos enterraria justamente os que importam.
    DESTAQUES = {
        "Campeões": theme.AZUL,
        "Em Risco": theme.LARANJA,
        "Perdidos": theme.AQUA,
    }
    fig = go.Figure()
    resto = rfm[~rfm["segmento"].isin(DESTAQUES)]
    fig.add_scatter(
        x=resto["recencia_dias"], y=resto["monetario"], mode="markers",
        name="Demais segmentos",
        marker=dict(color=theme.CINZA, size=7, opacity=0.6),
        hovertemplate="recência %{x} dias, R$ %{y:,.0f}<extra>outros</extra>",
    )
    for segmento, cor in DESTAQUES.items():
        d = rfm[rfm["segmento"] == segmento]
        fig.add_scatter(
            x=d["recencia_dias"], y=d["monetario"], mode="markers",
            name=segmento, marker=dict(color=cor, size=9),
            hovertemplate="recência %{x} dias, R$ %{y:,.0f}<extra>" + segmento + "</extra>",
        )
    fig.update_layout(
        title="Recência x Valor monetário por cliente",
        xaxis_title="Dias desde a última compra",
        yaxis_title="Receita total do cliente (R$)",
        height=460,
        hoverdistance=24,
    )
    with col_dir2:
        st.plotly_chart(fig, width="stretch", key="rfm_dispersao", config=ui.CONFIG_GRAFICO)
        ui.gemeo_tabular(rfm)


# ---- Aba Retencao -----------------------------------------------------------

with aba_ret:
    ui.nota_estrutural()

    matriz = (
        coorte.pivot(index="coorte_mes", columns="meses_desde", values="pct_retido")
        .sort_index()
    )
    fig = go.Figure(
        go.Heatmap(
            z=matriz.values,
            x=[str(c) for c in matriz.columns],
            y=[ui.rotulo_mes(m) for m in matriz.index],
            colorscale=RAMPA,
            zmin=0, zmax=100,
            colorbar=dict(title="% retido", outlinewidth=0),
            hovertemplate="coorte %{y}, mês %{x}: %{z}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="Retenção por coorte de primeira compra",
        xaxis_title="Meses desde a primeira compra",
        yaxis_title="Coorte (mês da primeira compra)",
        yaxis_autorange="reversed",
        height=560,
    )
    st.plotly_chart(fig, width="stretch", key="coorte_heatmap", config=ui.CONFIG_GRAFICO)
    ui.gemeo_tabular(coorte)

    fig = go.Figure(
        go.Scatter(
            x=curva["meses_desde"], y=curva["pct_medio"], mode="lines",
            line=dict(color=theme.AZUL, width=2), showlegend=False,
        )
    )
    fig.update_layout(
        title="Curva média de retenção",
        xaxis_title="Meses desde a primeira compra",
        yaxis_title="% médio retido",
        height=380,
    )
    st.plotly_chart(fig, width="stretch", key="curva_retencao", config=ui.CONFIG_GRAFICO)
    ui.gemeo_tabular(curva)
