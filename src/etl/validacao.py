"""Regras de validacao: decide o destino de cada linha do staging.

Linha invalida vai para a quarentena com motivo; duplicata de id_transacao e
descartada (mantem a primeira) e apenas logada; inconsistencia de caixa/acento
e normalizada, nao rejeitada. Outlier de preco permanece: e informacao de
negocio, nao dado quebrado.
"""

from src.etl import limpeza

CAMPOS_CHAVE = ["id_transacao", "id_cliente", "data_venda", "valor_unitario", "nome_produto"]


def valida_e_limpa(linhas):
    """Recebe as linhas cruas do staging (dicts de texto) e separa em tres destinos.

    Retorna (registros_limpos, rejeitados, n_duplicatas):
    - registros_limpos: dicts tipados prontos para a carga no dw
    - rejeitados: lista de (linha_original, motivo) para a quarentena
    - n_duplicatas: quantas linhas cairam por id_transacao repetido
    """
    limpos = []
    rejeitados = []
    ids_vistos = set()
    n_duplicatas = 0

    for linha in linhas:
        motivo = _motivo_rejeicao(linha)
        if motivo:
            rejeitados.append((linha, motivo))
            continue

        if linha["id_transacao"] in ids_vistos:
            n_duplicatas += 1
            continue
        ids_vistos.add(linha["id_transacao"])

        cidade, uf, pais = _parse_localidade(linha["localidade_venda"])
        limpos.append({
            "id_transacao": linha["id_transacao"].strip(),
            "id_pedido": linha["id_pedido"].strip(),
            "data_venda": limpeza.parse_data_multiformato(linha["data_venda"]),
            "id_cliente": linha["id_cliente"].strip(),
            "nome_produto": linha["nome_produto"].strip(),
            "categoria": limpeza.normaliza_categoria(linha["categoria_produto"]),
            "valor_unitario": round(limpeza.parse_moeda_brasileira(linha["valor_unitario"]), 2),
            "quantidade": int(linha["quantidade"]),
            "cidade": cidade,
            "uf": uf,
            "pais": pais,
            "metodo_pagamento": linha["metodo_pagamento"].strip(),
            "status_pedido": limpeza.normaliza_status(linha["status_pedido"]),
        })

    return limpos, rejeitados, n_duplicatas


def _motivo_rejeicao(linha):
    """Primeiro motivo de rejeicao encontrado, ou None se a linha e valida."""
    for campo in CAMPOS_CHAVE:
        valor = linha.get(campo)
        if valor is None or not valor.strip():
            return f"campo chave nulo: {campo}"

    if limpeza.parse_data_multiformato(linha["data_venda"]) is None:
        return "data invalida"

    valor = limpeza.parse_moeda_brasileira(linha["valor_unitario"])
    if valor is None:
        return "valor invalido"
    if valor < 0:
        return "valor negativo"

    try:
        quantidade = int(linha["quantidade"])
    except (TypeError, ValueError):
        return "quantidade invalida"
    if quantidade <= 0:
        return "quantidade nao positiva"

    if limpeza.normaliza_status(linha["status_pedido"]) is None:
        return "status invalido"

    if limpeza.normaliza_categoria(linha["categoria_produto"]) is None:
        return "categoria nula"

    return None


def _parse_localidade(texto):
    """'Cidade/UF/Pais' -> tupla; o gerador so emite essa forma."""
    partes = [p.strip() for p in (texto or "").split("/")]
    if len(partes) != 3 or not all(partes):
        return ("Desconhecida", "ND", "Brasil")
    return tuple(partes)
