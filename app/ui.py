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


def grafico(fig, *, key: str) -> None:
    """Aplica o template do modo corrente e renderiza. Unico caminho de grafico.

    O template vem por figura, e nao de `pio.templates.default`, porque o default
    e do processo e o tema e da sessao: dois usuarios em modos diferentes se
    pintariam um ao outro.
    """
    fig.update_layout(template=theme.paleta().TEMPLATE)
    st.plotly_chart(fig, width="stretch", key=key, config=CONFIG_GRAFICO)

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
    *,
    ajuda: str | None = None,
    serie: pd.Series | None = None,
    delta_texto: str | None = None,
    subiu: bool = True,
    bom: bool = True,
    key: str | None = None,
) -> None:
    """Stat tile: valor grande, delta com seta e cor de status, sparkline.

    Para um numero unico, o numero e o grafico - por isso tile e nao barra.
    As cores de status valem so para o delta, nunca para series.
    O texto de `ajuda` vira o tooltip do titulo; sem ele o Streamlit nao desenha icone.
    """
    cores = theme.paleta()
    with col.container(border=True):
        st.caption(titulo, help=ajuda)
        st.markdown(
            f"<div style='font-size:1.7rem;font-weight:600;line-height:1.15;"
            f"color:{cores.TINTA}'>{valor}</div>",
            unsafe_allow_html=True,
        )
        if delta_texto is not None:
            cor = cores.STATUS_BOM if bom else cores.STATUS_CRITICO
            seta = "&#8593;" if subiu else "&#8595;"
            st.markdown(
                f"<span style='color:{cor};font-size:0.9rem'>{seta} {delta_texto}"
                f"</span> <span style='color:{cores.ROTULO_EIXO};font-size:0.8rem'>"
                f"vs período anterior</span>",
                unsafe_allow_html=True,
            )
        if serie is not None and len(serie) > 1:
            fig = go.Figure(
                go.Scatter(
                    y=serie, mode="lines",
                    line=dict(color=cores.AZUL, width=2), hoverinfo="skip",
                )
            )
            fig.update_layout(
                template=cores.TEMPLATE,
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
        "Análise estrutural sobre a base completa de vendas concretizadas; "
        "não reage aos filtros da barra lateral."
    )


def leitura(texto: str) -> None:
    """Frase de conclusao sob um grafico. Slot fixo: abaixo do chart, acima do gemeo."""
    st.caption(texto)


# Marca tipografica do topo da sidebar. As tres linhas tem a mesma largura, e e o
# `textLength` do SVG que garante isso: ele estica cada linha ate a medida
# distribuindo a diferenca entre as letras, entao o retangulo fecha em qualquer
# sistema operacional, com a fonte que o navegador resolver. Em HTML seria um
# <span> por letra.
#
# 176px e o maior bloco que cabe centralizado nos 240px uteis da barra deixando
# livres os 32px que o botao de recolher ocupa a direita. 21px na primeira linha e
# o teto: "INSIGHTFLOW" em negrito mede ate 8x o corpo na fonte mais larga que um
# sistema entrega (DejaVu Sans), ou seja 168px - acima disso o lengthAdjust
# entraria em espacamento negativo e as letras se encostariam.
MARCA_LARGURA = 176
MARCA_ALTURA = 53

# Texto, baseline, corpo, peso e token de cor. As folgas verticais sao 0.454 do
# corpo de cada linha, entao o par de baixo se amarra (5.5px) e se descola do
# logotipo (9.5px) sem numero escolhido a mao. O descritor vai em maiuscula porque
# o tracking largo que a justificacao exige - 1.7em em PROJETO, que tem 7 letras
# contra as 10 de DESENVOLVE - le como lockup em caixa alta e como defeito de
# renderizacao em caixa de titulo.
_MARCA_LINHAS = (
    ("INSIGHTFLOW", 18, 21, 700, "AZUL"),
    ("PROJETO", 36, 12, 400, "TINTA_SECUNDARIA"),
    ("DESENVOLVE", 50, 12, 400, "TINTA_SECUNDARIA"),
)

# O unico ponto acima do menu de paginas e o cabecalho da barra, e quem escreve
# nele e o st.logo - que trava a altura da imagem em 32px. Estas tres regras
# destravam a altura e centralizam o bloco. A margem esquerda de 2rem espelha os
# 32px reservados pelo botao de recolher, que continua no canto sem ser tocado.
# O cabecalho tem altura fixa de 60px, menor que os 69px que a marca passou a pedir
# com 1rem de respiro em cima, entao ele vira `height:auto` e cresce com o conteudo -
# sem isso a margem empurraria a marca para fora em vez de afasta-la do topo. O
# min-height fica como guarda para o dia em que o Streamlit reduzir o numero nativo.
# Sao seletores privados do Streamlit: se mudarem, a marca volta a 32px e alinhada
# a esquerda - feia, legivel, sem estourar layout.
CSS_MARCA = f"""
<style>
[data-testid="stSidebarLogo"]{{height:{MARCA_ALTURA}px !important;
margin-top:1rem !important;margin-bottom:0 !important;width:100%;
object-position:center !important}}
[data-testid="stSidebarHeader"]{{height:auto;min-height:{MARCA_ALTURA}px}}
[data-testid="stSidebarHeader"]>*:first-child{{flex:1 1 auto;min-width:0;
margin-left:2rem}}
</style>
"""


def _envelope_svg(altura: int, conteudo: str) -> str:
    """Comeca exatamente em `<svg ` porque e o que a regex do Streamlit exige.

    Um espaco ou quebra de linha a mais no inicio e a string deixa de ser
    reconhecida como SVG e passa a ser tratada como caminho de arquivo. O `xmlns`
    vai explicito: sem ele o Streamlit injeta o dele.
    """
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {MARCA_LARGURA} {altura}" '
        f'width="{MARCA_LARGURA}" height="{altura}" '
        f'font-family="{theme.FONTE}">{conteudo}</svg>'
    )


def _linha_svg(texto: str, y: int, corpo: int, peso: int, cor: str) -> str:
    return (
        f'<text x="0" y="{y}" textLength="{MARCA_LARGURA}" lengthAdjust="spacing" '
        f'font-size="{corpo}" font-weight="{peso}" fill="{cor}">{texto}</text>'
    )


def _svg_marca(cores) -> str:
    """Bloco de tres linhas, para a barra aberta.

    A family vai no atributo do SVG, e nao em CSS: a imagem e servida dentro de um
    <img>, e ali o CSS da pagina nao alcanca o desenho. `lengthAdjust="spacing"`
    mexe so no avanco entre glifos; "spacingAndGlyphs" deformaria as letras.
    """
    linhas = "".join(
        _linha_svg(texto, y, corpo, peso, getattr(cores, token))
        for texto, y, corpo, peso, token in _MARCA_LINHAS
    )
    return _envelope_svg(MARCA_ALTURA, linhas)


def _svg_marca_compacta(cores) -> str:
    """So o logotipo, para o cabecalho do app com a barra recolhida.

    Ali o teto de 32px continua valendo e as duas linhas de baixo ficariam com 7px
    de corpo. Como a altura do viewBox e a altura renderizada sao as mesmas, a
    escala e 1:1 e a palavra sai do mesmo tamanho que sai na barra aberta: recolher
    a barra tira o descritor e mais nada.
    """
    texto, _, corpo, peso, token = _MARCA_LINHAS[0]
    return _envelope_svg(32, _linha_svg(texto, 23, corpo, peso, getattr(cores, token)))


def marca() -> None:
    """Marca no topo da sidebar, acima do menu de paginas.

    st.logo e a unica API que escreve no cabecalho da barra; tudo que passa por
    st.sidebar cai abaixo do menu. Ela aceita string SVG, que o Streamlit serializa
    como data URI - por isso a marca e gerada aqui, com as cores do modo corrente,
    em vez de ser um arquivo de imagem fixo.

    Sem `link=`: sem ele o Streamlit ja liga o logo a pagina inicial sozinho.
    """
    cores = theme.paleta()
    st.logo(
        _svg_marca(cores), size="large", icon_image=_svg_marca_compacta(cores)
    )
    st.html(CSS_MARCA)
