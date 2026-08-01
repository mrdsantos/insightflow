"""Paleta e templates Plotly do dashboard.

Unica fonte de verdade das cores do projeto. Nenhum grafico declara cor propria:
tudo vem da paleta que `paleta()` devolve para a sessao corrente.

Sao duas paletas, nao uma invertida. Modo escuro nao e o claro de cabeca para
baixo: os passos escuros foram escolhidos para a superficie escura e validados
contra ela (separacao sob daltonismo e contraste), do mesmo jeito que os claros
foram validados contra a clara. Numeros em docs/decisoes.md.

Quem escolhe o modo e o frontend, nao o Python - ver `paleta()`. Aqui so existem
os dois conjuntos de tokens e a pergunta de qual deles vale agora.
"""

from dataclasses import dataclass

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

FONTE = "system-ui, -apple-system, 'Segoe UI', sans-serif"

# Fundo transparente para sparklines embutidos em cards. Nao depende de modo:
# quem pinta o fundo ali e o card do Streamlit.
TRANSPARENTE = "rgba(0,0,0,0)"


@dataclass(frozen=True)
class Paleta:
    """Tokens de cor de um modo.

    Os dois modos preenchem os mesmos campos - e por isso que as paginas leem
    `cores.AZUL` sem saber em qual modo estao. Campo novo aqui obriga os dois
    modos a responderem, que e exatamente a garantia que se quer.
    """

    MODO: str
    TEMPLATE: str
    # Slots categoricos, nesta ordem fixa. Formas par-a-par (dispersao, bolha)
    # usam no maximo os slots 1-3; barras e linhas ate o 4 com rotulo direto.
    AZUL: str
    LARANJA: str
    AQUA: str
    AMARELO: str
    # Rampa sequencial (heatmaps), um matiz so. Nunca arco-iris. No escuro a
    # ordem inverte, porque quem precisa recuar para o fundo e a ponta escura.
    RAMPA_AZUL: tuple[str, ...]
    # Cinza de de-emphasis: o fundo neutro quando a historia destaca poucas series.
    CINZA: str
    # Status: so para o delta de KPI, nunca como cor de serie. O delta e texto
    # pequeno, entao aqui a barra e 4.5:1 e nao os 3:1 de marca - e por isso que
    # os dois modos usam passos diferentes.
    STATUS_BOM: str
    STATUS_CRITICO: str
    # Tinta e cromo
    SUPERFICIE: str
    PLANO: str
    TINTA: str
    TINTA_SECUNDARIA: str
    ROTULO_EIXO: str
    GRADE: str
    EIXO: str

    @property
    def SLOTS(self) -> list[str]:
        return [self.AZUL, self.LARANJA, self.AQUA, self.AMARELO]


CLARO = Paleta(
    MODO="claro",
    TEMPLATE="insightflow_claro",
    AZUL="#2a78d6",
    LARANJA="#eb6834",
    AQUA="#1baf7a",
    AMARELO="#eda100",
    RAMPA_AZUL=(
        "#cde2fb",
        "#9ec5f4",
        "#6da7ec",
        "#3987e5",
        "#2a78d6",
        "#256abf",
        "#184f95",
        "#0d366b",
    ),
    CINZA="#c3c2b7",
    STATUS_BOM="#006300",
    STATUS_CRITICO="#d03b3b",
    SUPERFICIE="#fcfcfb",
    PLANO="#f9f9f7",
    TINTA="#0b0b0b",
    TINTA_SECUNDARIA="#52514e",
    ROTULO_EIXO="#898781",
    GRADE="#e1e0d9",
    EIXO="#c3c2b7",
)

ESCURO = Paleta(
    MODO="escuro",
    TEMPLATE="insightflow_escuro",
    AZUL="#3987e5",
    LARANJA="#d95926",
    AQUA="#199e70",
    AMARELO="#c98500",
    RAMPA_AZUL=tuple(reversed(CLARO.RAMPA_AZUL)),
    CINZA="#52514e",
    STATUS_BOM="#0ca30c",
    STATUS_CRITICO="#e66767",
    SUPERFICIE="#1a1a19",
    PLANO="#0d0d0d",
    TINTA="#ffffff",
    TINTA_SECUNDARIA="#c3c2b7",
    ROTULO_EIXO="#898781",
    GRADE="#2c2c2a",
    EIXO="#383835",
)


def _template(p: Paleta) -> go.layout.Template:
    eixo = dict(
        showgrid=True,
        gridcolor=p.GRADE,
        gridwidth=1,
        showline=True,
        linecolor=p.EIXO,
        linewidth=1,
        ticks="outside",
        tickcolor=p.EIXO,
        tickfont=dict(color=p.ROTULO_EIXO, size=12),
        title=dict(font=dict(color=p.TINTA_SECUNDARIA, size=13)),
        zeroline=False,
    )
    return go.layout.Template(
        layout=go.Layout(
            colorway=p.SLOTS,
            # pt-BR: virgula decimal, ponto de milhar. Sem isso o hover sai 1,234,567.
            separators=",.",
            paper_bgcolor=p.SUPERFICIE,
            plot_bgcolor=p.SUPERFICIE,
            font=dict(family=FONTE, color=p.TINTA, size=13),
            # Titulo preso ao topo da figura, nao ao meio da margem: com y automatico
            # ele caia na mesma faixa da legenda horizontal e os dois se sobrepunham.
            title=dict(
                font=dict(size=15, color=p.TINTA),
                x=0,
                xanchor="left",
                yref="container",
                y=1.0,
                yanchor="top",
                pad=dict(t=12),
            ),
            xaxis=eixo,
            yaxis=eixo,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(color=p.TINTA_SECUNDARIA, size=12),
            ),
            hoverlabel=dict(
                bgcolor=p.SUPERFICIE,
                bordercolor=p.EIXO,
                font=dict(family=FONTE, color=p.TINTA, size=12),
            ),
            # Faixa superior larga o bastante para titulo e legenda empilhados, uniforme
            # em todo grafico para as areas de plotagem lado a lado nao desalinharem.
            margin=dict(l=8, r=8, t=76, b=8),
        )
    )


# Os dois templates ficam registrados; nenhum e o default. `pio.templates.default`
# e estado do processo, e tema aqui e por sessao - com dois usuarios em modos
# diferentes o default de um pintaria o grafico do outro. Quem aplica o template
# por figura e `ui.grafico`.
MODOS = {CLARO.MODO: CLARO, ESCURO.MODO: ESCURO}
for _p in MODOS.values():
    pio.templates[_p.TEMPLATE] = _template(_p)


def paleta() -> Paleta:
    """Paleta do modo que o frontend esta de fato pintando.

    O Streamlit resolve o tema sozinho no boot e nao aceita ordem do Python: o
    unico gancho e `embed_options` na URL, que o `st.query_params` nem enxerga.
    Entao o Python nao decide o modo - ele pergunta qual saiu e devolve a paleta
    correspondente. Uma autoridade so e o que impede o chrome e o grafico de
    divergirem, que era o bug de quando este modulo decidia por conta propria.

    `type` vem None quando nao ha navegador do outro lado (AppTest, boot sem
    sessao); cai no claro, o mesmo fallback que o frontend usa sem `matchMedia`.
    """
    return ESCURO if st.context.theme.type == "dark" else CLARO
