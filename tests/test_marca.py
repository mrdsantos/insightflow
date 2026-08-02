"""Guardas da marca tipografica da sidebar, sem banco e sem navegador.

A marca e um SVG gerado em tempo de execucao e entregue ao st.logo como string.
Isso tem tres modos de falha que nao aparecem em teste de pagina: a string deixar
de ser reconhecida como SVG (e virar caminho de arquivo, com excecao em runtime),
as tres linhas saierem com larguras diferentes (o retangulo e o requisito), e o
SVG carregar a cor do modo errado.
"""

import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "app"))

import theme  # noqa: E402  (depende do sys.path acima, como as paginas)
import ui  # noqa: E402

# A mesma regex de streamlit/elements/lib/image_utils.py. Se a string nao casar
# aqui, o Streamlit tenta abrir o SVG como arquivo e st.logo levanta excecao.
SVG = re.compile(r"(^\s?(<\?xml[\s\S]*<svg\s)|^\s?<svg\s|^\s?<svg>\s)")


@pytest.mark.parametrize("modo", ["claro", "escuro"])
@pytest.mark.parametrize("construtor", ["_svg_marca", "_svg_marca_compacta"])
def test_svg_e_reconhecido_como_svg(modo, construtor):
    svg = getattr(ui, construtor)(theme.MODOS[modo])
    assert SVG.search(svg), f"{construtor} nao comeca em <svg: {svg[:40]!r}"
    assert "xmlns" in svg


def test_as_tres_linhas_tem_a_mesma_largura():
    """O bloco retangular e o pedido; quem o entrega e o textLength de cada linha."""
    svg = ui._svg_marca(theme.CLARO)
    assert svg.count(f'textLength="{ui.MARCA_LARGURA}"') == 3
    assert svg.count('lengthAdjust="spacing"') == 3
    for texto, *_ in ui._MARCA_LINHAS:
        assert f">{texto}</text>" in svg


@pytest.mark.parametrize("modo,outro", [("claro", "escuro"), ("escuro", "claro")])
def test_marca_usa_as_cores_do_modo_corrente(modo, outro):
    """Sem isso a marca ficaria com o azul do claro sobre o fundo escuro."""
    p, q = theme.MODOS[modo], theme.MODOS[outro]
    svg = ui._svg_marca(p)
    assert p.AZUL in svg
    assert p.TINTA_SECUNDARIA in svg
    assert q.AZUL not in svg
    assert q.TINTA_SECUNDARIA not in svg


def test_css_da_marca_declara_os_seletores_privados():
    """O CSS depende de contrato privado do Streamlit, e isto deixa isso por escrito.

    Nao ha como testar que os seletores ainda existem no bundle - o .venv nao vai
    para o Docker. O que este teste guarda e a intencao: se alguem apagar as regras
    achando que sao decorativas, a marca volta silenciosamente para 32px de altura
    e alinhada a esquerda.
    """
    assert "stSidebarLogo" in ui.CSS_MARCA
    assert "stSidebarHeader" in ui.CSS_MARCA
    assert f"{ui.MARCA_ALTURA}px" in ui.CSS_MARCA
