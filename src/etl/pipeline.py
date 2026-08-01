"""Pipeline completo: CSV -> staging -> validacao -> dw. Uso: python -m src.etl.pipeline

Full refresh idempotente: rodar duas vezes deixa as contagens identicas.
"""

import logging
import os
from collections import Counter
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from src.etl import carga, limpeza, validacao

RAIZ = Path(__file__).resolve().parent.parent.parent
CAMINHO_CSV = RAIZ / "dados" / "ecom_data.csv"
CAMINHO_RELATORIO = RAIZ / "docs" / "relatorio_qualidade.md"

log = logging.getLogger("etl")


def executa(url=None):
    load_dotenv(RAIZ / ".env")
    url = url or os.environ["DATABASE_URL"]

    with psycopg.connect(url) as conn:
        n_staging = carga.carrega_staging(conn, CAMINHO_CSV)
        log.info("extract: %s linhas do csv para o staging", n_staging)

        linhas = carga.le_staging(conn)
        limpos, rejeitados, n_duplicatas = validacao.valida_e_limpa(linhas)
        log.info("transform: %s validas, %s rejeitadas, %s duplicatas descartadas",
                 len(limpos), len(rejeitados), n_duplicatas)

        n_calendario = carga.garante_calendario(conn)
        if n_calendario:
            log.info("load: dim_calendario populada com %s dias", n_calendario)
        dims = carga.carrega_dimensoes(conn, limpos)
        log.info("load: dims recarregadas %s", dims)
        n_fato = carga.carrega_fato(conn, limpos)
        n_quarentena = carga.carrega_quarentena(conn, rejeitados)
        log.info("load: %s linhas no fato, %s na quarentena", n_fato, n_quarentena)

        resumo = {
            "staging": n_staging,
            "validas": len(limpos),
            "rejeitadas": len(rejeitados),
            "duplicatas": n_duplicatas,
            "fato": n_fato,
            "quarentena": n_quarentena,
            "dims": dims,
        }
        _gera_relatorio(linhas, limpos, rejeitados, resumo)
        log.info("relatorio de qualidade regenerado em %s", CAMINHO_RELATORIO)

    return resumo


def _formato_data(texto):
    if texto is None or not texto.strip():
        return "nulo"
    t = texto.strip()
    if limpeza.parse_data_multiformato(t) is None:
        return "invalido"
    if "-" in t and t[:4].isdigit():
        return "iso (aaaa-mm-dd)"
    return "dd/mm/aaaa" if "/" in t else "dd-mm-aaaa"


def _formato_moeda(texto):
    if texto is None or not texto.strip():
        return "nulo"
    t = texto.strip()
    if limpeza.parse_moeda_brasileira(t) is None:
        return "invalido"
    if t.startswith("R$"):
        return "R$ 1.234,56"
    return "1.234,56" if "," in t else "1234.56"


def _gera_relatorio(linhas, limpos, rejeitados, resumo):
    """Reescreve docs/relatorio_qualidade.md com o antes/depois desta execucao."""
    nulos = {c: sum(1 for l in linhas if not (l[c] or "").strip())
             for c in carga.COLUNAS_STAGING}
    formatos_data = Counter(_formato_data(l["data_venda"]) for l in linhas)
    formas_moeda = Counter(_formato_moeda(l["valor_unitario"]) for l in linhas)
    categorias_antes = {(l["categoria_produto"] or "").strip() for l in linhas}
    status_antes = {(l["status_pedido"] or "").strip() for l in linhas}
    motivos = Counter(motivo for _, motivo in rejeitados)
    pct = 100 * resumo["rejeitadas"] / resumo["staging"]
    pct_br = f"{pct:.1f}".replace(".", ",")

    txt = [
        "# Relatório de qualidade dos dados",
        "",
        "Gerado pelo pipeline a cada execução - não editar na mão. "
        "Sem timestamp de propósito: execução idêntica gera arquivo idêntico.",
        "",
        "## Visão geral",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Linhas no CSV / staging | {resumo['staging']} |",
        f"| Linhas válidas carregadas no fato | {resumo['fato']} |",
        f"| Linhas rejeitadas (quarentena) | {resumo['rejeitadas']} ({pct_br}%) |",
        f"| Duplicatas de id_transacao descartadas | {resumo['duplicatas']} |",
        f"| Clientes / produtos / localidades distintos | {resumo['dims']['clientes']} / "
        f"{resumo['dims']['produtos']} / {resumo['dims']['localidades']} |",
        "",
        "## Antes da limpeza",
        "",
        "### Nulos por coluna (staging)",
        "",
        "| Coluna | Nulos |",
        "|---|---|",
        *[f"| {c} | {n} |" for c, n in nulos.items() if n > 0],
        "",
        "### Formatos de data em circulação",
        "",
        "| Formato | Linhas |",
        "|---|---|",
        *[f"| {f} | {n} |" for f, n in formatos_data.most_common()],
        "",
        "### Formas de moeda em circulação",
        "",
        "| Forma | Linhas |",
        "|---|---|",
        *[f"| {f} | {n} |" for f, n in formas_moeda.most_common()],
        "",
        "### Inconsistências de texto",
        "",
        f"- Categorias distintas antes da normalização: {len(categorias_antes)}",
        f"- Status distintos antes da normalização: {len(status_antes)}",
        "",
        "## Depois da limpeza",
        "",
        f"- Categorias distintas no dw: {len({r['categoria'] for r in limpos})}",
        f"- Status distintos no dw: {len({r['status_pedido'] for r in limpos})}",
        "- Nulos em campo chave no fato: 0 (barrados na validação)",
        "- Datas e valores: tipados (DATE / NUMERIC), um formato só",
        "",
        "## Quarentena por motivo",
        "",
        "| Motivo | Linhas |",
        "|---|---|",
        *[f"| {m} | {n} |" for m, n in motivos.most_common()],
        "",
    ]
    CAMINHO_RELATORIO.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_RELATORIO.write_text("\n".join(txt), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    executa()
