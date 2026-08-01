"""Guarda app/definicoes.py contra drift do SQL e dos titulos das paginas.

Estatico e sem banco, no mesmo espirito de test_ordem_views.py: nome de segmento
com acento errado nao levanta excecao em lugar nenhum, so mente na tela.
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
APP = RAIZ / "app"
sys.path.insert(0, str(APP))

import definicoes  # noqa: E402

RE_CASE = re.compile(r"(?:THEN|ELSE)\s+'([^']+)'")
RE_DEFINE = re.compile(r"CREATE\s+OR\s+REPLACE\s+VIEW\s+dw\.(\w+)", re.IGNORECASE)


def test_segmentos_na_ordem_do_case_do_sql():
    sql = (RAIZ / "sql" / "views" / "006_vw_rfm.sql").read_text(encoding="utf-8")
    assert [s["segmento"] for s in definicoes.SEGMENTOS] == RE_CASE.findall(sql)


def test_toda_view_citada_existe_em_sql_views():
    definidas = set()
    for arquivo in (RAIZ / "sql" / "views").glob("*.sql"):
        definidas.update(RE_DEFINE.findall(arquivo.read_text(encoding="utf-8")))
    for kpi in definicoes.KPIS:
        assert kpi["view"] in definidas, (
            f"{kpi['slug']} cita dw.{kpi['view']}, que nao e criada em sql/views/"
        )


def test_titulo_do_tile_ainda_aparece_na_pagina():
    for kpi in definicoes.KPIS:
        texto = (APP / kpi["arquivo"]).read_text(encoding="utf-8")
        alvo = kpi["ancora"] or kpi["nome"]
        assert alvo in texto, (
            f"{kpi['slug']}: '{alvo}' sumiu de app/{kpi['arquivo']}. O titulo do tile "
            "mudou e a tabela da pagina Definicoes ficou desatualizada."
        )


def test_dezesseis_kpis_com_slug_unico():
    slugs = [k["slug"] for k in definicoes.KPIS]
    assert len(definicoes.KPIS) == 16
    assert len(set(slugs)) == 16
