"""Pagina 3 - Produtos."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(page_title="InsightFlow - Produtos", layout="wide")

import dados
import definicoes
import filtros
import theme
import ui

st.title("O que vender mais e o que descontinuar?")

op = filtros.opcoes()
sel = filtros.sidebar(op)

vendas = filtros.aplicar(dados.ler_view("vw_vendas"), sel)
pareto = dados.ler_view("vw_pareto_produtos")
cresc = filtros.aplicar(
    dados.ler_view("vw_crescimento_categoria"), sel, quais=("periodo", "categoria")
)
prod_met = dados.ler_view("vw_produtos_metricas")

if vendas.empty:
    st.warning("Nenhum dado no recorte selecionado. Ajuste os filtros.")
    st.stop()


# ---- KPIs -------------------------------------------------------------------

por_categoria = vendas.groupby("categoria")["valor_total"].sum()
n_top20 = max(1, round(0.2 * len(pareto)))
concentracao = pareto.loc[pareto["posicao"] == n_top20, "pct_acumulado"].iloc[0]

c1, c2, c3, c4 = st.columns(4)
ui.stat_tile(
    c1, "SKUs ativos no recorte", ui.fmt_num(vendas["nome_produto"].nunique()),
    ajuda=definicoes.ajuda("skus_ativos"),
)
ui.stat_tile(
    c2, "Categoria líder no recorte", por_categoria.idxmax(),
    ajuda=definicoes.ajuda("categoria_lider"),
)
ui.stat_tile(
    c3, "Produto líder (base completa)", pareto.iloc[0]["produto"],
    ajuda=definicoes.ajuda("produto_lider"),
)
ui.stat_tile(
    c4,
    f"Concentração: top 20% dos produtos ({n_top20} SKUs)",
    ui.fmt_pct(concentracao),
    ajuda=definicoes.ajuda("concentracao_top20"),
)


# ---- Pareto em escala unica -------------------------------------------------
# Pareto classico poe % acumulado num segundo eixo Y; eixo duplo e proibido no
# projeto. Com barras em % do total e linha em % acumulado, as duas medidas
# compartilham a escala 0-100 e o eixo unico nao perde informacao nenhuma.

ui.nota_estrutural()

fig = go.Figure()
fig.add_bar(
    x=pareto["produto"], y=pareto["pct_faturamento"],
    name="Participação no faturamento (%)", marker_color=theme.AZUL,
)
fig.add_scatter(
    x=pareto["produto"], y=pareto["pct_acumulado"], mode="lines",
    name="Acumulado (%)", line=dict(color=theme.LARANJA, width=2),
)
fig.add_hline(y=80, line_color=theme.CINZA, line_width=1)
fig.add_annotation(
    x=1.0, xref="paper", y=80, yanchor="bottom", xanchor="right",
    text="80%", showarrow=False, font=dict(color=theme.TINTA_SECUNDARIA, size=12),
)
fig.update_layout(
    title="Pareto de produtos: participação e acumulado na mesma escala",
    yaxis=dict(title="% do faturamento total", range=[0, 105]),
    height=480,
)
fig.update_xaxes(tickangle=-45)
st.plotly_chart(fig, width="stretch", key="pareto", config=ui.CONFIG_GRAFICO)
ui.gemeo_tabular(pareto)


# ---- Crescimento MoM por categoria: small multiples -------------------------
# Facetar e a resposta quando ha mais categorias que o teto de cores: uma linha
# por painel, mesma escala Y, em vez de seis linhas sobrepostas.

categorias = sorted(cresc["categoria"].unique())
if categorias:
    n_col = 3
    n_lin = -(-len(categorias) // n_col)
    fig = make_subplots(
        rows=n_lin, cols=n_col, shared_yaxes=True,
        subplot_titles=categorias, vertical_spacing=0.16,
    )
    for i, categoria in enumerate(categorias):
        d = cresc[cresc["categoria"] == categoria].sort_values("ano_mes")
        fig.add_scatter(
            x=pd.to_datetime(d["ano_mes"] + "-01"), y=d["mom_pct"],
            mode="lines", line=dict(color=theme.AZUL, width=2),
            showlegend=False, name=categoria,
            row=i // n_col + 1, col=i % n_col + 1,
            customdata=d["ano_mes"].map(ui.rotulo_mes),
            hovertemplate="%{customdata}: %{y:.1f}%<extra>" + categoria + "</extra>",
        )
    fig.add_hline(y=0, line_color=theme.EIXO, line_width=1)
    fig.update_layout(
        title="Crescimento MoM por categoria (%)", height=220 * n_lin + 80
    )
    fig.update_xaxes(**ui.eixo_mes(cresc["ano_mes"], passo=6, como_data=True))
    fig.update_annotations(font=dict(size=12, color=theme.TINTA_SECUNDARIA))
    st.plotly_chart(fig, width="stretch", key="mom_categorias", config=ui.CONFIG_GRAFICO)
    ui.gemeo_tabular(cresc)


# ---- Matriz crescimento x faturamento ---------------------------------------

ui.nota_estrutural()

validos = prod_met.dropna(subset=["crescimento_pct"]).reset_index(drop=True)
destaques = {}
for rotulo, idx, cor in [
    ("maior volume", validos["faturamento"].idxmax(), theme.AZUL),
    ("maior crescimento", validos["crescimento_pct"].idxmax(), theme.LARANJA),
    ("maior queda", validos["crescimento_pct"].idxmin(), theme.AQUA),
]:
    produto = validos.loc[idx, "produto"]
    if produto not in destaques:
        destaques[produto] = (rotulo, cor)

resto = validos[~validos["produto"].isin(destaques)]
fig = go.Figure()
fig.add_scatter(
    x=resto["faturamento"], y=resto["crescimento_pct"], mode="markers",
    name="Demais produtos", marker=dict(color=theme.CINZA, size=8, opacity=0.7),
    hovertemplate="%{customdata}: R$ %{x:,.0f}, %{y}%<extra></extra>",
    customdata=resto["produto"],
)
for produto, (rotulo, cor) in destaques.items():
    d = validos[validos["produto"] == produto]
    fig.add_scatter(
        x=d["faturamento"], y=d["crescimento_pct"], mode="markers+text",
        name=f"{produto} ({rotulo})", marker=dict(color=cor, size=11),
        text=[produto], textposition="top center",
        textfont=dict(color=theme.TINTA_SECUNDARIA, size=12),
        hovertemplate="%{text}: R$ %{x:,.0f}, %{y}%<extra></extra>",
        cliponaxis=False,
    )
fig.add_hline(y=0, line_color=theme.EIXO, line_width=1)
fig.update_layout(
    title="Crescimento (últimos 3 meses vs 3 anteriores) x faturamento total",
    xaxis_title="Faturamento total (R$)",
    yaxis_title="Crescimento (%)",
    height=480,
    hoverdistance=24,
)
st.plotly_chart(fig, width="stretch", key="matriz_produtos", config=ui.CONFIG_GRAFICO)
ui.gemeo_tabular(prod_met)
