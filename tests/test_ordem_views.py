"""Garante que sql/views/ aplica na ordem de dependencia - o migrate.py so faz sorted()."""

import re
from pathlib import Path

PASTA_VIEWS = Path(__file__).resolve().parent.parent / "sql" / "views"

RE_DEFINE = re.compile(r"CREATE\s+OR\s+REPLACE\s+VIEW\s+dw\.(\w+)", re.IGNORECASE)
RE_REFERENCIA = re.compile(r"(?:FROM|JOIN)\s+dw\.(vw_\w+)", re.IGNORECASE)


def test_dependencia_vem_antes_no_sorted():
    ja_definidas = set()
    # mesma ordenacao que scripts/migrate.py usa para aplicar
    for arquivo in sorted(PASTA_VIEWS.glob("*.sql")):
        sql = arquivo.read_text(encoding="utf-8")
        for referida in RE_REFERENCIA.findall(sql):
            assert referida in ja_definidas, (
                f"{arquivo.name} le dw.{referida}, que ainda nao foi criada nesta ordem. "
                "Em banco zerado o migrate.py quebra aqui."
            )
        ja_definidas.update(RE_DEFINE.findall(sql))
