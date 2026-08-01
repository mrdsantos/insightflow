"""Testes das funcoes puras de limpeza - os formatos vem do gerador de sujeira."""

from datetime import date

import pytest

from src.etl.limpeza import (
    normaliza_categoria,
    normaliza_status,
    parse_data_multiformato,
    parse_moeda_brasileira,
)


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("R$ 1.234,56", 1234.56),
        ("1.234,56", 1234.56),
        ("1234.56", 1234.56),
        ("222,79", 222.79),
        ("R$ 89,90", 89.90),
        ("R$ 12.345.678,90", 12345678.90),
    ],
)
def test_parse_moeda_brasileira(entrada, esperado):
    assert parse_moeda_brasileira(entrada) == esperado


@pytest.mark.parametrize("invalido", ["R$ ???", "gratis", "1,2,3", "", None])
def test_parse_moeda_rejeita_lixo(invalido):
    assert parse_moeda_brasileira(invalido) is None


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("2025-03-07", date(2025, 3, 7)),
        ("07/03/2025", date(2025, 3, 7)),
        ("07-03-2025", date(2025, 3, 7)),
    ],
)
def test_parse_data_multiformato(entrada, esperado):
    assert parse_data_multiformato(entrada) == esperado


@pytest.mark.parametrize("invalida", ["31/02/2025", "2025-13-07", "00/00/0000", "sem data", "", None])
def test_parse_data_rejeita_invalida(invalida):
    assert parse_data_multiformato(invalida) is None


def test_normaliza_categoria():
    assert normaliza_categoria("ELETRONICOS") == "Eletronicos"
    assert normaliza_categoria("eletronicos") == "Eletronicos"
    assert normaliza_categoria("Eletrônicos") == "Eletronicos"
    assert normaliza_categoria("Acessórios") == "Acessorios"
    assert normaliza_categoria("  Casa  ") == "Casa"


def test_normaliza_status():
    assert normaliza_status("ENTREGUE") == "Entregue"
    assert normaliza_status("entregue") == "Entregue"
    assert normaliza_status("Devolvido") == "Devolvido"
    # status fora do dominio nao e normalizavel: vai virar quarentena
    assert normaliza_status("Em analise") is None
    assert normaliza_status("Extraviado") is None
