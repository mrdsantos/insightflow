"""Pagina 1 - Visao Geral."""

import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="InsightFlow - Visão Geral", layout="wide")

import dados
import definicoes
import filtros
import theme
import ui

cores = theme.paleta()

st.title("Como o negócio está performando e para onde está indo?")
st.caption(
    "Painel de vendas de um e-commerce simulado, do faturamento ao modelo de previsão. "
    "A definição de cada número está na página Definições, na barra lateral."
)

op = filtros.opcoes()
sel = filtros.sidebar(op)

kpis = dados.ler_view("vw_kpis_mensais")
kpis_per = filtros.aplicar(kpis, sel, quais=("periodo",))
fat = filtros.aplicar(dados.ler_view("vw_faturamento_mensal"), sel)

if kpis_per.empty or fat.empty:
    st.warning("Nenhum dado no recorte selecionado. Ajuste os filtros.")
    st.stop()


# ---- KPIs: janela selecionada vs janela anterior de mesmo tamanho ----------

def janela_anterior(base: "pd.DataFrame", atual: "pd.DataFrame") -> "pd.DataFrame":
    antes = base[base["ano_mes"] < atual["ano_mes"].min()]
    return antes.tail(len(atual))


ant = janela_anterior(kpis, kpis_per)

fat_atual = kpis_per["faturamento"].sum()
ticket_atual = kpis_per["faturamento"].sum() / kpis_per["pedidos"].sum()
ret_atual = kpis_per["taxa_retencao"].mean()
churn_atual = kpis_per["churn_rate"].mean()

mensal = kpis_per.sort_values("ano_mes")

if ant.empty:
    deltas = {k: None for k in ("fat", "ticket", "ret", "churn")}
else:
    fat_ant = ant["faturamento"].sum()
    ticket_ant = ant["faturamento"].sum() / ant["pedidos"].sum()
    deltas = {
        "fat": 100 * (fat_atual - fat_ant) / fat_ant,
        "ticket": 100 * (ticket_atual - ticket_ant) / ticket_ant,
        "ret": ret_atual - ant["taxa_retencao"].mean(),
        "churn": churn_atual - ant["churn_rate"].mean(),
    }

c1, c2, c3, c4 = st.columns(4)
d = deltas["fat"]
ui.stat_tile(
    c1, "Faturamento Total", ui.fmt_compacto(fat_atual),
    ajuda=definicoes.ajuda("faturamento_total"),
    serie=mensal["faturamento"], key="spark_fat",
    delta_texto=None if d is None else ui.fmt_pct(abs(d)),
    subiu=d is not None and d >= 0, bom=d is not None and d >= 0,
)
d = deltas["ticket"]
ui.stat_tile(
    c2, "Ticket Médio", ui.fmt_moeda(ticket_atual, 2),
    ajuda=definicoes.ajuda("ticket_medio"),
    serie=mensal["ticket_medio"], key="spark_ticket",
    delta_texto=None if d is None else ui.fmt_pct(abs(d)),
    subiu=d is not None and d >= 0, bom=d is not None and d >= 0,
)
d = deltas["ret"]
ui.stat_tile(
    c3, "Taxa de Retenção", ui.fmt_pct(ret_atual),
    ajuda=definicoes.ajuda("taxa_retencao"),
    serie=mensal["taxa_retencao"], key="spark_ret",
    delta_texto=None if d is None else f"{ui.fmt_num(abs(d), 1)} p.p.",
    subiu=d is not None and d >= 0, bom=d is not None and d >= 0,
)
d = deltas["churn"]
ui.stat_tile(
    c4, "Churn Rate", ui.fmt_pct(churn_atual),
    ajuda=definicoes.ajuda("churn_rate"),
    serie=mensal["churn_rate"], key="spark_churn",
    delta_texto=None if d is None else f"{ui.fmt_num(abs(d), 1)} p.p.",
    subiu=d is not None and d >= 0, bom=d is not None and d <= 0,
)


# ---- Serie temporal de faturamento mensal ----------------------------------

serie = fat.groupby("ano_mes", as_index=False)["faturamento"].sum().sort_values("ano_mes")

fig = go.Figure()
fig.add_scatter(
    x=serie["ano_mes"], y=serie["faturamento"], mode="lines",
    line=dict(color=cores.AZUL, width=2), name="Faturamento", showlegend=False,
)
ultimo = serie.iloc[-1]
fig.add_scatter(
    x=[ultimo["ano_mes"]], y=[ultimo["faturamento"]],
    mode="markers+text", text=[ui.fmt_compacto(ultimo["faturamento"])],
    textposition="top center", textfont=dict(color=cores.TINTA_SECUNDARIA),
    marker=dict(color=cores.AZUL, size=8),
    showlegend=False, hoverinfo="skip", cliponaxis=False,
)
fig.update_layout(title="Faturamento mensal", height=380)
fig.update_xaxes(type="category", **ui.eixo_mes(serie["ano_mes"], passo=2))
ui.grafico(fig, key="serie_mensal")
if len(serie) < 2:
    texto = "Recorte de um único mês; não há série para comparar pico e média."
else:
    pico = serie.loc[serie["faturamento"].idxmax()]
    acima = 100 * pico["faturamento"] / serie["faturamento"].mean() - 100
    texto = (
        f"O pico do recorte é {ui.rotulo_mes(pico['ano_mes'])}, com "
        f"{ui.fmt_compacto(pico['faturamento'])}, {ui.fmt_pct(acima)} acima da média "
        "mensal. O crescimento vem em degraus de patamar, não em rampa."
    )
ui.leitura(texto)
ui.gemeo_tabular(serie)


# ---- Sazonalidade ano a ano -------------------------------------------------

col_esq, col_dir = st.columns(2)

saz = fat.groupby(["ano", "mes"], as_index=False)["faturamento"].sum()
# teto de 3 series coloridas: com mais anos no recorte, mostra os 3 ultimos
anos = sorted(saz["ano"].unique())[-3:]
fig = go.Figure()
for i, ano in enumerate(anos):
    d = saz[saz["ano"] == ano].sort_values("mes")
    fig.add_scatter(
        x=[ui.MESES[m - 1] for m in d["mes"]], y=d["faturamento"],
        mode="lines", name=str(ano),
        line=dict(color=cores.SLOTS[i], width=2),
    )
fig.update_layout(title="Sazonalidade ano a ano", height=380)
fig.update_xaxes(categoryorder="array", categoryarray=ui.MESES)
with col_esq:
    ui.grafico(fig, key="sazonalidade")
    if len(anos) < 2 or fat["ano_mes"].nunique() < 12:
        texto = (
            "Recorte curto para sazonalidade: a forma que se repete só aparece com "
            "pelo menos dois ciclos completos de doze meses."
        )
    else:
        por_mes = saz.groupby("mes", as_index=False)["faturamento"].sum()
        alto = por_mes.loc[por_mes["faturamento"].idxmax()]
        baixo = por_mes.loc[por_mes["faturamento"].idxmin()]
        mes_alto = ui.MESES[int(alto["mes"]) - 1]
        mes_baixo = ui.MESES[int(baixo["mes"]) - 1]
        vezes = ui.fmt_num(alto["faturamento"] / baixo["faturamento"], 1)
        texto = (
            f"O melhor mês do calendário é {mes_alto} e o pior é {mes_baixo}, e "
            f"{mes_alto} soma {vezes} vezes o faturamento de {mes_baixo}. "
            "O mês de pico é evento de calendário, não patamar novo."
        )
    ui.leitura(texto)
    ui.gemeo_tabular(saz)


# ---- Faturamento por categoria ----------------------------------------------

cat = (
    fat.groupby("categoria", as_index=False)["faturamento"].sum()
    .sort_values("faturamento")
)
fig = go.Figure(
    go.Bar(
        x=cat["faturamento"], y=cat["categoria"], orientation="h",
        marker_color=cores.AZUL, name="Faturamento", showlegend=False,
    )
)
fig.update_layout(title="Faturamento por categoria", height=380)
with col_dir:
    ui.grafico(fig, key="categorias")
    if len(cat) < 2:
        texto = "Uma única categoria no recorte; não há concentração a comparar."
    else:
        # cat esta ordenado ascendente: a lider e a ultima linha, nao a primeira
        lider = cat.iloc[-1]
        pct = 100 * lider["faturamento"] / cat["faturamento"].sum()
        acum = cat["faturamento"].iloc[:-1].cumsum().to_numpy()
        abertura = f"{lider['categoria']} responde por {ui.fmt_pct(pct)} do faturamento"
        if acum[-1] >= lider["faturamento"]:
            n = int((acum < lider["faturamento"]).sum()) + 1
            texto = f"{abertura} do recorte, o mesmo que as {n} menores categorias somadas."
        else:
            texto = f"{abertura} do recorte, mais do que todas as outras somadas."
    ui.leitura(texto)
    ui.gemeo_tabular(cat.sort_values("faturamento", ascending=False))
