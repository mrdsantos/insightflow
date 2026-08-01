"""Pagina 4 - Previsao."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="InsightFlow - Previsão", layout="wide")

import dados
import filtros
import theme
import ui

st.title("Quanto vou faturar no próximo mês, e o quanto posso confiar nisso?")

op = filtros.opcoes()
filtros.sidebar(op)

st.caption(
    "Página estrutural: o modelo usa a série mensal completa de vendas concretizadas "
    "e não reage aos filtros da barra lateral."
)

prev = dados.ler_view("vw_previsao").sort_values("ano_mes").reset_index(drop=True)
met = dados.ler_view("vw_metricas_modelo")
for col in ("realizado", "ajustado", "previsto", "banda_inf", "banda_sup"):
    prev[col] = prev[col].astype(float)
for col in ("mae", "mape", "r2"):
    met[col] = met[col].astype(float)

realizado = prev[prev["realizado"].notna()]
teste = prev[prev["fase"] == "teste"]
futuro = prev[prev["fase"] == "futuro"]
reg = met[met["modelo"] == "regressao"].iloc[0]

# ---- KPIs -------------------------------------------------------------------

proximo = futuro.iloc[0]
c1, c2, c3, c4 = st.columns(4)
ui.stat_tile(c1, f"Previsão para {ui.rotulo_mes(proximo['ano_mes'])}",
             ui.fmt_compacto(proximo["previsto"]))
ui.stat_tile(c2, "MAE da regressão (teste)", ui.fmt_compacto(reg["mae"]))
ui.stat_tile(c3, "MAPE da regressão (teste)", ui.fmt_pct(reg["mape"]))
ui.stat_tile(c4, "R2 da regressão (teste)", ui.fmt_num(reg["r2"], 2))
st.caption(
    f"Banda da previsão: {ui.fmt_compacto(proximo['banda_inf'])} a "
    f"{ui.fmt_compacto(proximo['banda_sup'])} (1,96 desvios do resíduo de teste). "
    "Métricas medidas nos 6 meses de teste (jan-jun/2026), fora do treino."
)


# ---- Historico + ajuste + projecao ------------------------------------------
# Unico tracejado permitido no projeto: aqui ele e semantico, significa projecao.

datas_realizado = pd.to_datetime(realizado["ano_mes"] + "-01")
datas_teste = pd.to_datetime(teste["ano_mes"] + "-01")
# projecao e banda partem do ultimo mes realizado para a linha nao nascer no ar
emenda = realizado.iloc[-1]
datas_futuro = pd.to_datetime(
    pd.concat([pd.Series([emenda["ano_mes"]]), futuro["ano_mes"]]) + "-01"
)
linha_previsto = pd.concat([pd.Series([emenda["realizado"]]), futuro["previsto"]])
rot_futuro = pd.concat([pd.Series([emenda["ano_mes"]]), futuro["ano_mes"]]).map(ui.rotulo_mes)

fig = go.Figure()
fig.add_scatter(
    x=datas_futuro, y=pd.concat([pd.Series([emenda["realizado"]]), futuro["banda_sup"]]),
    mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip",
)
fig.add_scatter(
    x=datas_futuro, y=pd.concat([pd.Series([emenda["realizado"]]), futuro["banda_inf"]]),
    mode="lines", line=dict(width=0), fill="tonexty", fillcolor=theme.RAMPA_AZUL[0],
    name="Banda (1,96 desvios do resíduo)", hoverinfo="skip",
)
fig.add_scatter(
    x=datas_realizado, y=realizado["realizado"], mode="lines",
    name="Realizado", line=dict(color=theme.AZUL, width=2),
    customdata=realizado["ano_mes"].map(ui.rotulo_mes),
    hovertemplate="%{customdata}: R$ %{y:,.0f}<extra>Realizado</extra>",
)
fig.add_scatter(
    x=datas_teste, y=teste["ajustado"], mode="lines",
    name="Ajustado no teste", line=dict(color=theme.LARANJA, width=2),
    customdata=teste["ano_mes"].map(ui.rotulo_mes),
    hovertemplate="%{customdata}: R$ %{y:,.0f}<extra>Ajustado no teste</extra>",
)
fig.add_scatter(
    x=datas_futuro, y=linha_previsto, mode="lines",
    name="Projeção", line=dict(color=theme.AZUL, width=2, dash="dash"),
    customdata=rot_futuro,
    hovertemplate="%{customdata}: R$ %{y:,.0f}<extra>Projeção</extra>",
)
for fase, inicio in [("teste", teste["ano_mes"].iloc[0]), ("projeção", futuro["ano_mes"].iloc[0])]:
    x = pd.Timestamp(inicio + "-01")
    fig.add_vline(x=x, line_color=theme.GRADE, line_width=1)
    # rotulo por dentro do grafico: ancorado por baixo ele subia para a faixa da legenda
    fig.add_annotation(
        x=x, y=1.0, yref="paper", yanchor="top", xanchor="left",
        text=fase, showarrow=False, font=dict(color=theme.ROTULO_EIXO, size=11),
    )
fig.update_layout(
    title="Faturamento mensal: realizado, ajuste no teste e projeção",
    yaxis_title="Faturamento (R$)",
    height=460,
)
fig.update_xaxes(**ui.eixo_mes(prev["ano_mes"], passo=3, como_data=True))
st.plotly_chart(fig, width="stretch", key="previsao", config=ui.CONFIG_GRAFICO)
ui.gemeo_tabular(prev)


# ---- Modelo vs baseline: tabela, nao grafico --------------------------------
# Para seis numeros, duas barras seriam anti-padrao; a tabela e mais rapida de ler.

st.subheader("Modelo vs baseline no mesmo teste")
NOMES = {"media_movel": "Média móvel (3 meses)", "regressao": "Regressão linear (tendência + mês)"}
tabela = pd.DataFrame({
    "Modelo": met["modelo"].map(NOMES),
    "MAE": met["mae"].map(lambda v: ui.fmt_moeda(v)),
    "MAPE": met["mape"].map(lambda v: ui.fmt_pct(v)),
    "R2": met["r2"].map(lambda v: ui.fmt_num(v, 2)),
})
st.dataframe(tabela, width="stretch", hide_index=True)

st.markdown(
    """
**Leitura do resultado.** No teste (jan-jun/2026), o baseline ingênuo ganhou da regressão
por pouco: 2026 abriu num patamar acima do que 2025 sugeria, e a média móvel, que só olha
os 3 meses anteriores, se adaptou ao salto mais rápido do que uma tendência estimada em
18 meses. O R2 negativo dos dois é o número mais importante da tabela: nenhum dos modelos
prevê bem mês a mês com 24 observações de histórico.

A projeção acima usa a regressão mesmo assim, porque é o único dos dois modelos com
estrutura sazonal: média móvel projetada para frente converge para uma reta e jamais
anteciparia o pico de novembro. **Limitações:** banda constante no horizonte (dez/2026 é
mais incerto que jul/2026 e a banda não mostra isso), sazonalidade média de apenas dois
anos, nenhuma variável externa. O número serve como ordem de grandeza para planejamento,
não como meta. Análise completa no notebook `03_modelo.ipynb` e em `docs/decisoes.md`.
"""
)
