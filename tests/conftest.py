"""Duble do sinal de tema que vem do navegador.

`theme.paleta()` pergunta ao frontend qual modo saiu, por `st.context.theme.type`,
e esse valor chega junto do rerun do navegador. Em teste nao ha navegador: o
AppTest constroi o ScriptRunContext com `context_info=None` fixo e nao expoe onde
mudar isso. Sem este duble o modo escuro ficaria sem cobertura nenhuma.
"""

import pytest
from streamlit.runtime.context import ContextProxy, StreamlitTheme


@pytest.fixture
def modo_do_frontend(monkeypatch):
    """Devolve uma funcao que fixa o `type` de st.context.theme ("dark", "light", None)."""

    def aplicar(tipo: str | None) -> None:
        monkeypatch.setattr(
            ContextProxy,
            "theme",
            property(lambda self: StreamlitTheme({"type": tipo})),
        )

    return aplicar
