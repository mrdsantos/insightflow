"""Gerador de dados sinteticos de e-commerce.

Produz dados/ecom_data.csv com seed fixa: duas execucoes geram bytes identicos.
Sazonalidade (novembro alto) e tendencia de crescimento sao plantadas de proposito
para as analises do bloco 2 terem o que encontrar.

A sujeira e aplicada por cima dos dados limpos com taxas fixas (constantes TAXA_*),
para a quarentena esperada ficar previsivel e o relatorio de qualidade virar
evidencia, nao surpresa.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20260731
RAIZ = Path(__file__).resolve().parent.parent.parent
CAMINHO_SAIDA = RAIZ / "dados" / "ecom_data.csv"

INICIO = date(2024, 7, 1)
MESES = 24  # jul/2024 -> jun/2026

# (nome, categoria, preco_base)
PRODUTOS = [
    ("Notebook Gamer", "Eletronicos", 4890.00),
    ("Notebook Ultrafino", "Eletronicos", 3450.00),
    ("Smartphone X200", "Eletronicos", 2199.00),
    ("Smart TV 50", "Eletronicos", 2590.00),
    ("Tablet 10", "Eletronicos", 1290.00),
    ("Monitor 27", "Eletronicos", 1150.00),
    ("Mouse Sem Fio", "Acessorios", 89.90),
    ("Teclado Mecanico", "Acessorios", 349.00),
    ("Headset Gamer", "Acessorios", 259.00),
    ("Mochila para Notebook", "Acessorios", 179.00),
    ("Hub USB-C", "Acessorios", 129.00),
    ("Capa para Smartphone", "Acessorios", 49.90),
    ("Carregador Turbo", "Acessorios", 99.00),
    ("Tenis Corrida Leve", "Esporte", 329.00),
    ("Camiseta Dry Fit", "Esporte", 79.90),
    ("Garrafa Termica", "Esporte", 119.00),
    ("Tapete de Yoga", "Esporte", 149.00),
    ("Halteres 10kg", "Esporte", 189.00),
    ("Cafeteira Eletrica", "Casa", 289.00),
    ("Aspirador Robo", "Casa", 1590.00),
    ("Jogo de Panelas", "Casa", 399.00),
    ("Liquidificador Potente", "Casa", 219.00),
    ("Luminaria de Mesa", "Casa", 139.00),
    ("Livro Dados em Acao", "Livros", 89.00),
    ("Livro SQL Essencial", "Livros", 79.00),
    ("Livro Historia do Brasil", "Livros", 69.90),
    ("Camisa Social Slim", "Moda", 159.00),
    ("Calca Jeans Reta", "Moda", 189.00),
    ("Vestido Midi", "Moda", 219.00),
    ("Jaqueta Corta Vento", "Moda", 269.00),
]

# afinidades plantadas: quem compra o item da esquerda tende a levar os da direita
AFINIDADES = {
    "Notebook Gamer": ["Mouse Sem Fio", "Mochila para Notebook", "Headset Gamer"],
    "Notebook Ultrafino": ["Mouse Sem Fio", "Hub USB-C", "Mochila para Notebook"],
    "Smartphone X200": ["Capa para Smartphone", "Carregador Turbo"],
    "Tenis Corrida Leve": ["Camiseta Dry Fit", "Garrafa Termica"],
    "Cafeteira Eletrica": ["Liquidificador Potente"],
    "Tapete de Yoga": ["Garrafa Termica", "Halteres 10kg"],
}

LOCALIDADES = [
    ("Sao Paulo", "SP"), ("Campinas", "SP"), ("Santos", "SP"),
    ("Rio de Janeiro", "RJ"), ("Niteroi", "RJ"),
    ("Belo Horizonte", "MG"), ("Uberlandia", "MG"),
    ("Curitiba", "PR"), ("Porto Alegre", "RS"), ("Florianopolis", "SC"),
    ("Salvador", "BA"), ("Recife", "PE"), ("Fortaleza", "CE"),
    ("Brasilia", "DF"), ("Goiania", "GO"),
]
# pesos: sudeste concentra a operacao
PESOS_LOCALIDADE = [18, 7, 5, 12, 4, 9, 4, 8, 7, 5, 6, 5, 4, 4, 2]

METODOS_PAGAMENTO = ["Cartao de Credito", "Pix", "Boleto", "Cartao de Debito"]
PESOS_PAGAMENTO = [42, 33, 13, 12]

STATUS = ["Entregue", "Enviado", "Processando", "Cancelado", "Devolvido"]
PESOS_STATUS = [78, 6, 4, 8, 4]

N_CLIENTES = 700
PEDIDOS_BASE_MES = 139      # pedidos no primeiro mes
CRESCIMENTO_MENSAL = 0.016  # tendencia suave

# multiplicador por mes-do-ano: novembro (black friday) alto, dezembro aquecido
SAZONALIDADE = {1: 0.92, 2: 0.88, 3: 0.95, 4: 0.97, 5: 1.02, 6: 0.98,
                7: 0.96, 8: 0.99, 9: 1.00, 10: 1.05, 11: 1.75, 12: 1.30}

# taxas de sujeira (fracao das linhas atingidas)
TAXA_NULOS = 0.03
TAXA_DUPLICATAS = 0.015
TAXA_QTD_NEGATIVA = 0.010
TAXA_STATUS_INVALIDO = 0.005
TAXA_DATA_QUEBRADA = 0.005
TAXA_MOEDA_QUEBRADA = 0.004
TAXA_OUTLIER_PRECO = 0.006
TAXA_CAIXA_CATEGORIA = 0.15
TAXA_CAIXA_STATUS = 0.08

COLUNAS_NULAVEIS = ["ID_Cliente", "Data_Venda", "Valor_Unitario", "Nome_Produto", "ID_Transacao"]

VARIANTES_CATEGORIA = {
    "Eletronicos": ["ELETRONICOS", "eletronicos", "Eletrônicos"],
    "Acessorios": ["ACESSORIOS", "acessorios", "Acessórios"],
    "Esporte": ["ESPORTE", "esporte"],
    "Casa": ["CASA", "casa"],
    "Livros": ["LIVROS", "livros"],
    "Moda": ["MODA", "moda"],
}
STATUS_INVALIDOS = ["Em analise", "Aguardando pagamento", "Extraviado"]
DATAS_QUEBRADAS = ["31/02/2025", "2025-13-07", "00/00/0000", "sem data"]
MOEDAS_QUEBRADAS = ["R$ ???", "gratis", "1,2,3"]


def _formata_moeda(valor, forma):
    """Devolve o valor numa das 3 formas que circulam no CSV."""
    inteiro, centavos = f"{valor:.2f}".split(".")
    milhar = ""
    while len(inteiro) > 3:
        milhar = "." + inteiro[-3:] + milhar
        inteiro = inteiro[:-3]
    com_milhar = inteiro + milhar
    if forma == "brl":
        return f"R$ {com_milhar},{centavos}"
    if forma == "decimal_virgula":
        return f"{com_milhar},{centavos}"
    return f"{valor:.2f}"


def _suja(linhas, rng):
    """Aplica a sujeira linha a linha com as taxas fixas e injeta duplicatas."""
    formatos_data = ["iso", "br_barra", "br_traco"]
    formas_moeda = ["brl", "decimal_virgula", "ponto"]

    for linha in linhas:
        # outlier de preco: legitimo, permanece no fato (nao vai para quarentena)
        valor = float(linha["Valor_Unitario"])
        if rng.random() < TAXA_OUTLIER_PRECO:
            valor = round(valor * rng.uniform(6, 12), 2)

        forma = rng.choices(formas_moeda, weights=[40, 25, 35], k=1)[0]
        linha["Valor_Unitario"] = _formata_moeda(valor, forma)

        formato = rng.choices(formatos_data, weights=[60, 25, 15], k=1)[0]
        d = date.fromisoformat(linha["Data_Venda"])
        if formato == "br_barra":
            linha["Data_Venda"] = d.strftime("%d/%m/%Y")
        elif formato == "br_traco":
            linha["Data_Venda"] = d.strftime("%d-%m-%Y")

        if rng.random() < TAXA_CAIXA_CATEGORIA:
            linha["Categoria_Produto"] = rng.choice(VARIANTES_CATEGORIA[linha["Categoria_Produto"]])

        if rng.random() < TAXA_CAIXA_STATUS:
            linha["Status_Pedido"] = rng.choice([linha["Status_Pedido"].upper(),
                                                 linha["Status_Pedido"].lower()])
        if rng.random() < TAXA_STATUS_INVALIDO:
            linha["Status_Pedido"] = rng.choice(STATUS_INVALIDOS)

        if rng.random() < TAXA_QTD_NEGATIVA:
            linha["Quantidade"] = rng.choice([-1, -2, 0])

        if rng.random() < TAXA_DATA_QUEBRADA:
            linha["Data_Venda"] = rng.choice(DATAS_QUEBRADAS)
        if rng.random() < TAXA_MOEDA_QUEBRADA:
            linha["Valor_Unitario"] = rng.choice(MOEDAS_QUEBRADAS)

        if rng.random() < TAXA_NULOS:
            linha[rng.choice(COLUNAS_NULAVEIS)] = ""

    # duplicatas exatas de id_transacao espalhadas pelo arquivo
    n_dup = int(len(linhas) * TAXA_DUPLICATAS)
    for _ in range(n_dup):
        original = rng.choice(linhas)
        linhas.insert(rng.randrange(len(linhas)), dict(original))
    return linhas


def _gera_clientes(rng):
    """Clientes com peso de atividade e janela de vida, para RFM e coorte terem sinal."""
    clientes = []
    for i in range(1, N_CLIENTES + 1):
        # mes de entrada concentrado no inicio, mas com chegada continua (coortes novas)
        mes_entrada = min(int(rng.expovariate(1 / 8)), MESES - 1)
        duracao = 3 + int(rng.expovariate(1 / 10))  # alguns churnam cedo
        mes_saida = min(mes_entrada + duracao, MESES - 1)
        clientes.append({
            "id": f"CLI{i:05d}",
            "peso": rng.lognormvariate(0, 0.9),  # poucos clientes pesados
            "localidade": rng.choices(LOCALIDADES, weights=PESOS_LOCALIDADE, k=1)[0],
            "mes_entrada": mes_entrada,
            "mes_saida": mes_saida,
        })
    return clientes


def _escolhe_itens(rng):
    """1 a 5 itens por pedido, com afinidades plantadas a partir do primeiro item."""
    primeiro = rng.choices(PRODUTOS, weights=[3 if p[1] != "Eletronicos" else 2 for p in PRODUTOS], k=1)[0]
    itens = [primeiro]
    n_extras = rng.choices([0, 1, 2, 3, 4], weights=[45, 28, 15, 8, 4], k=1)[0]
    afins = AFINIDADES.get(primeiro[0], [])
    catalogo = {p[0]: p for p in PRODUTOS}
    for _ in range(n_extras):
        if afins and rng.random() < 0.65:
            nome = rng.choice(afins)
            candidato = catalogo[nome]
        else:
            candidato = rng.choice(PRODUTOS)
        if candidato not in itens:
            itens.append(candidato)
    return itens


def gerar(caminho=CAMINHO_SAIDA):
    rng = random.Random(SEED)
    clientes = _gera_clientes(rng)
    linhas = []
    n_transacao = 0
    n_pedido = 0

    for m in range(MESES):
        ano = INICIO.year + (INICIO.month - 1 + m) // 12
        mes = (INICIO.month - 1 + m) % 12 + 1
        n_pedidos = int(PEDIDOS_BASE_MES * (1 + CRESCIMENTO_MENSAL) ** m * SAZONALIDADE[mes])

        ativos = [c for c in clientes if c["mes_entrada"] <= m <= c["mes_saida"]]
        pesos = [c["peso"] for c in ativos]
        dias_no_mes = ((date(ano + (mes == 12), mes % 12 + 1, 1)) - date(ano, mes, 1)).days

        for _ in range(n_pedidos):
            cliente = rng.choices(ativos, weights=pesos, k=1)[0]
            dia = rng.randint(1, dias_no_mes)
            data_venda = date(ano, mes, dia)
            n_pedido += 1
            id_pedido = f"PED{n_pedido:06d}"
            cidade, uf = cliente["localidade"]
            metodo = rng.choices(METODOS_PAGAMENTO, weights=PESOS_PAGAMENTO, k=1)[0]
            status = rng.choices(STATUS, weights=PESOS_STATUS, k=1)[0]

            for nome, categoria, preco_base in _escolhe_itens(rng):
                n_transacao += 1
                preco = round(preco_base * rng.uniform(0.95, 1.08), 2)
                quantidade = rng.choices([1, 2, 3, 4], weights=[70, 20, 7, 3], k=1)[0]
                linhas.append({
                    "ID_Transacao": f"TRX{n_transacao:07d}",
                    "ID_Pedido": id_pedido,
                    "Data_Venda": data_venda.isoformat(),
                    "ID_Cliente": cliente["id"],
                    "Nome_Produto": nome,
                    "Categoria_Produto": categoria,
                    "Valor_Unitario": f"{preco:.2f}",
                    "Quantidade": quantidade,
                    "Localidade_Venda": f"{cidade}/{uf}/Brasil",
                    "Metodo_Pagamento": metodo,
                    "Status_Pedido": status,
                })

    linhas = _suja(linhas, random.Random(SEED + 1))

    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        # lineterminator LF: o repo normaliza para LF, e assim o arquivo regenerado
        # bate byte a byte com o commitado em qualquer plataforma
        escritor = csv.DictWriter(f, fieldnames=list(linhas[0].keys()), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)
    return len(linhas)


if __name__ == "__main__":
    total = gerar()
    print(f"gerado {CAMINHO_SAIDA} com {total} linhas")
