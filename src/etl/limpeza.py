"""Funcoes puras de limpeza: parse de moeda e data, normalizacao de texto.

Sem I/O e sem estado de proposito - sao as funcoes cobertas pelos testes.
Retorno None significa "nao parseia": quem decide o destino (quarentena) e a
validacao, nao este modulo.
"""

import unicodedata
from datetime import datetime

FORMATOS_DATA = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]

STATUS_VALIDOS = {"Entregue", "Enviado", "Processando", "Cancelado", "Devolvido"}


def parse_moeda_brasileira(texto):
    """Converte as formas em circulacao no CSV para float.

    Aceita 'R$ 1.234,56', '1.234,56', '222,79' e '1234.56'.
    Regra: virgula presente -> virgula e o decimal e ponto e milhar;
    so ponto -> decimal (o gerador nunca emite ponto de milhar sem virgula).
    """
    if texto is None:
        return None
    limpo = texto.replace("R$", "").strip()
    if not limpo:
        return None
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    try:
        valor = float(limpo)
    except ValueError:
        return None
    return valor


def parse_data_multiformato(texto):
    """Tenta os 3 formatos conhecidos ('2025-03-07', '07/03/2025', '07-03-2025')."""
    if texto is None:
        return None
    limpo = texto.strip()
    for formato in FORMATOS_DATA:
        try:
            return datetime.strptime(limpo, formato).date()
        except ValueError:
            continue
    return None


def _sem_acento(texto):
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def normaliza_categoria(texto):
    """'ELETRONICOS', 'eletronicos' e 'Eletrônicos' viram 'Eletronicos'."""
    if texto is None:
        return None
    limpo = _sem_acento(texto.strip())
    if not limpo:
        return None
    return limpo.capitalize()


def normaliza_status(texto):
    """Normaliza caixa/acento e devolve o status canonico, ou None se invalido."""
    if texto is None:
        return None
    candidato = _sem_acento(texto.strip()).capitalize()
    return candidato if candidato in STATUS_VALIDOS else None
