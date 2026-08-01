"""Guardas do tema, sem banco e sem navegador.

Coisas que quebram em silencio quando alguem mexe em tema: o config.toml sair de
sincronia com app/theme.py (TOML nao le Python, entao os hex estao duplicados de
proposito), o `pio.templates.default` voltar - ele e do processo e o tema e da
sessao -, uma cor solta aparecer fora do theme.py, e o Python voltar a decidir o
modo por conta propria em vez de perguntar ao frontend.
"""

import re
import sys
import tomllib
from pathlib import Path

import plotly.io as pio
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "app"))

import theme  # noqa: E402  (depende do sys.path acima, como as paginas)

CONFIG = tomllib.loads((RAIZ / ".streamlit" / "config.toml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("modo", ["claro", "escuro"])
def test_template_do_modo_esta_registrado(modo):
    p = theme.MODOS[modo]
    assert p.TEMPLATE in pio.templates
    assert pio.templates[p.TEMPLATE].layout.colorway == tuple(p.SLOTS)


def test_nenhum_template_e_o_default():
    """`pio.templates.default` e global do processo; tema aqui e por sessao.

    Com dois usuarios em modos diferentes, o default de um pintaria o grafico do
    outro. Quem aplica o template por figura e ui.grafico().
    """
    assert pio.templates.default not in {p.TEMPLATE for p in theme.MODOS.values()}


def test_os_dois_modos_tem_hex_proprios():
    """Escuro nao e o claro reaproveitado: os passos foram escolhidos para o fundo escuro."""
    iguais = {
        campo
        for campo in ("AZUL", "LARANJA", "AQUA", "AMARELO", "CINZA", "SUPERFICIE",
                      "PLANO", "TINTA", "TINTA_SECUNDARIA", "GRADE", "EIXO",
                      "STATUS_BOM", "STATUS_CRITICO")
        if getattr(theme.CLARO, campo) == getattr(theme.ESCURO, campo)
    }
    assert not iguais, f"passos repetidos entre os modos: {sorted(iguais)}"
    # ROTULO_EIXO e o unico invariante, e e assim na paleta de referencia.
    assert theme.CLARO.ROTULO_EIXO == theme.ESCURO.ROTULO_EIXO


def test_rampa_escura_e_a_clara_ao_contrario():
    """No escuro quem recua para o fundo e a ponta escura, entao a ordem inverte.

    E o que faz o passo 0 - usado como preenchimento da banda da previsao - ser o
    mais proximo da superficie nos dois modos, sem a pagina saber de nada.
    """
    assert theme.ESCURO.RAMPA_AZUL == tuple(reversed(theme.CLARO.RAMPA_AZUL))


@pytest.mark.parametrize(
    "secao,paleta,pares",
    [
        ("theme", "CLARO", {"primaryColor": "AZUL", "backgroundColor": "SUPERFICIE",
                            "secondaryBackgroundColor": "PLANO", "textColor": "TINTA"}),
        ("dark", "ESCURO", {"primaryColor": "AZUL", "backgroundColor": "SUPERFICIE",
                            "secondaryBackgroundColor": "PLANO", "textColor": "TINTA"}),
    ],
)
def test_config_toml_espelha_o_theme_py(secao, paleta, pares):
    bloco = CONFIG["theme"] if secao == "theme" else CONFIG["theme"]["dark"]
    p = getattr(theme, paleta)
    for chave, campo in pares.items():
        assert bloco[chave] == getattr(p, campo), (
            f"[{secao}] {chave} = {bloco[chave]} mas theme.{paleta}.{campo} = "
            f"{getattr(p, campo)}"
        )


@pytest.mark.parametrize(
    "tipo,esperado", [("dark", "escuro"), ("light", "claro"), (None, "claro")]
)
def test_paleta_segue_o_frontend(tipo, esperado, modo_do_frontend):
    """Quem decide o modo e o frontend; o Python so pergunta qual saiu.

    Enquanto o theme.py decidia sozinho, uma URL sem `embed_options` deixava o
    chrome escuro (o "Custom Theme Auto" do Streamlit segue o sistema) e o grafico
    claro. Sem navegador do outro lado, `type` e None e vale o claro.
    """
    modo_do_frontend(tipo)
    assert theme.paleta().MODO == esperado


def test_toggle_declara_embed_options_nos_dois_sentidos():
    """Sem `embed_options` o frontend cai no Auto e segue o sistema operacional.

    Era o que fazia o "Tema claro" nao voltar em quem estava com o sistema no
    escuro. O `tema=` proprio saiu junto: o frontend nunca o leu.
    """
    sys.path.insert(0, str(RAIZ / "app"))
    import filtros  # noqa: PLC0415  (mesmo import plano das paginas)

    assert set(filtros.DESTINO_TEMA) == set(theme.MODOS)
    for destino in filtros.DESTINO_TEMA.values():
        assert "embed_options=" in destino
        assert "tema=" not in destino
    assert filtros.DESTINO_TEMA["claro"] != filtros.DESTINO_TEMA["escuro"]


COR = re.compile(r"#[0-9a-fA-F]{6}\b|\brgba?\(")


def test_nenhuma_cor_fora_do_theme_py():
    fora = [
        f"{p.relative_to(RAIZ)}:{i}"
        for p in RAIZ.joinpath("app").rglob("*.py")
        if p.name != "theme.py"
        for i, linha in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
        if COR.search(linha)
    ]
    assert not fora, f"cor declarada fora de app/theme.py: {fora}"
