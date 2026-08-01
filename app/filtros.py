"""Sidebar global de filtros, com estado preservado entre paginas.

Uma unica barra para o dashboard inteiro: filtro por grafico ou por pagina quebra a
comparacao, porque dois graficos passam a mostrar recortes diferentes sem avisar.
Os presets de periodo sao ancorados na ultima venda da base, nao no relogio: o
dataset e um snapshot congelado e "ultimos 30 dias" a partir de hoje seria vazio.

Cada view declara no contrato de dados a quais filtros responde; as paginas passam
isso no parametro `quais` de aplicar(). As views estruturais (RFM, coorte, Pareto,
metricas de produto, top 10%) nao passam por aqui.
"""

import datetime as dt

import pandas as pd
import streamlit as st

import dados

STATUS_CONCRETIZADA = ["Entregue", "Enviado"]

PRESETS = [
    "Tudo",
    "Ultimos 30 dias",
    "Ultimos 90 dias",
    "Ultimos 180 dias",
    "Ano corrente",
    "Personalizado",
]


def opcoes() -> dict:
    """Valores distintos e janela de datas, lidos de vw_vendas (cacheado)."""
    v = dados.ler_view("vw_vendas")
    datas = pd.to_datetime(v["data_venda"])
    return {
        "categorias": sorted(v["categoria"].unique()),
        "ufs": sorted(v["uf"].unique()),
        "status": sorted(v["status_pedido"].unique()),
        "data_min": datas.min().date(),
        "data_max": datas.max().date(),
    }


def _defaults(op: dict) -> dict:
    return {
        "flt_preset": "Tudo",
        "flt_ini": op["data_min"],
        "flt_fim": op["data_max"],
        "flt_categorias": [],
        "flt_ufs": [],
        "flt_status": [s for s in STATUS_CONCRETIZADA if s in op["status"]],
    }


def _limpar(op: dict) -> None:
    for chave, valor in _defaults(op).items():
        st.session_state[chave] = valor


def _periodo(op: dict) -> tuple[dt.date, dt.date]:
    preset = st.session_state["flt_preset"]
    fim = op["data_max"]
    if preset == "Tudo":
        return op["data_min"], fim
    if preset == "Ultimos 30 dias":
        return fim - dt.timedelta(days=30), fim
    if preset == "Ultimos 90 dias":
        return fim - dt.timedelta(days=90), fim
    if preset == "Ultimos 180 dias":
        return fim - dt.timedelta(days=180), fim
    if preset == "Ano corrente":
        return dt.date(fim.year, 1, 1), fim
    return st.session_state["flt_ini"], st.session_state["flt_fim"]


def sidebar(op: dict) -> dict:
    """Renderiza a sidebar e devolve a selecao corrente.

    Chaves fixas em st.session_state; como a sidebar aparece em toda pagina,
    o Streamlit preserva o estado na navegacao.
    """
    for chave, valor in _defaults(op).items():
        st.session_state.setdefault(chave, valor)

    with st.sidebar:
        st.subheader("Filtros")
        st.selectbox("Periodo", PRESETS, key="flt_preset")
        if st.session_state["flt_preset"] == "Personalizado":
            st.date_input(
                "De", key="flt_ini", min_value=op["data_min"], max_value=op["data_max"]
            )
            st.date_input(
                "Ate", key="flt_fim", min_value=op["data_min"], max_value=op["data_max"]
            )
        st.caption(f"Presets contam a partir da ultima venda da base: {op['data_max']:%d/%m/%Y}")
        st.multiselect(
            "Categoria", op["categorias"], key="flt_categorias", placeholder="Todas"
        )
        st.multiselect("UF", op["ufs"], key="flt_ufs", placeholder="Todas")
        st.multiselect(
            "Status do pedido",
            op["status"],
            key="flt_status",
            help="Padrao: apenas venda concretizada (Entregue e Enviado).",
        )
        st.button("Limpar filtros", on_click=_limpar, args=(op,))

    ini, fim = _periodo(op)
    return {
        "periodo": (ini, fim),
        "categorias": st.session_state["flt_categorias"],
        "ufs": st.session_state["flt_ufs"],
        "status": st.session_state["flt_status"],
    }


def aplicar(
    df: pd.DataFrame,
    sel: dict,
    quais: tuple = ("periodo", "categoria", "uf", "status"),
) -> pd.DataFrame:
    """Aplica a selecao como filtro simples (o equivalente de um WHERE)."""
    out = df
    if "periodo" in quais:
        ini, fim = sel["periodo"]
        if "data_venda" in out.columns:
            datas = pd.to_datetime(out["data_venda"])
            out = out[(datas >= pd.Timestamp(ini)) & (datas <= pd.Timestamp(fim))]
        elif "ano_mes" in out.columns:
            out = out[
                (out["ano_mes"] >= ini.strftime("%Y-%m"))
                & (out["ano_mes"] <= fim.strftime("%Y-%m"))
            ]
    if "categoria" in quais and sel["categorias"] and "categoria" in out.columns:
        out = out[out["categoria"].isin(sel["categorias"])]
    if "uf" in quais and sel["ufs"] and "uf" in out.columns:
        out = out[out["uf"].isin(sel["ufs"])]
    if "status" in quais and sel["status"]:
        col = "status" if "status" in out.columns else "status_pedido"
        if col in out.columns:
            out = out[out[col].isin(sel["status"])]
    return out
