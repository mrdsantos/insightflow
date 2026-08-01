"""Paleta e template Plotly do dashboard.

Unica fonte de verdade das cores do projeto. Nenhum grafico declara cor propria:
tudo vem das constantes daqui e do template registrado como default no import.
Valores validados para daltonismo e contraste (paleta de referencia, sem alteracao).
"""

import plotly.graph_objects as go
import plotly.io as pio

# Slots categoricos, nesta ordem fixa. Formas par-a-par (dispersao, bolha)
# usam no maximo os slots 1-3; barras e linhas ate o 4 com rotulo direto.
AZUL = "#2a78d6"
LARANJA = "#eb6834"
AQUA = "#1baf7a"
AMARELO = "#eda100"
SLOTS = [AZUL, LARANJA, AQUA, AMARELO]

# Rampa sequencial (heatmaps), azul claro -> escuro. Nunca arco-iris.
RAMPA_AZUL = [
    "#cde2fb",
    "#9ec5f4",
    "#6da7ec",
    "#3987e5",
    "#2a78d6",
    "#256abf",
    "#184f95",
    "#0d366b",
]

# Cinza de de-emphasis: o fundo neutro quando a historia destaca poucas series.
CINZA = "#c3c2b7"

# Status: so para delta de KPI, nunca como cor de serie.
STATUS_BOM = "#0ca30c"
STATUS_CRITICO = "#d03b3b"

# Tinta e cromo
SUPERFICIE = "#fcfcfb"
PLANO = "#f9f9f7"
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
ROTULO_EIXO = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"

FONTE = "system-ui, -apple-system, 'Segoe UI', sans-serif"

# Fundo transparente para sparklines embutidos em cards.
TRANSPARENTE = "rgba(0,0,0,0)"

_eixo_padrao = dict(
    showgrid=True,
    gridcolor=GRADE,
    gridwidth=1,
    showline=True,
    linecolor=EIXO,
    linewidth=1,
    ticks="outside",
    tickcolor=EIXO,
    tickfont=dict(color=ROTULO_EIXO, size=12),
    title=dict(font=dict(color=TINTA_SECUNDARIA, size=13)),
    zeroline=False,
)

_template = go.layout.Template(
    layout=go.Layout(
        colorway=SLOTS,
        paper_bgcolor=SUPERFICIE,
        plot_bgcolor=SUPERFICIE,
        font=dict(family=FONTE, color=TINTA, size=13),
        title=dict(font=dict(size=15, color=TINTA), x=0, xanchor="left"),
        xaxis=_eixo_padrao,
        yaxis=_eixo_padrao,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(color=TINTA_SECUNDARIA, size=12),
        ),
        hoverlabel=dict(
            bgcolor=SUPERFICIE,
            bordercolor=EIXO,
            font=dict(family=FONTE, color=TINTA, size=12),
        ),
        margin=dict(l=8, r=8, t=48, b=8),
    )
)

pio.templates["insightflow"] = _template
pio.templates.default = "insightflow"
