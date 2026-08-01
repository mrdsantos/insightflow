"""Fonte unica do texto de definicao do dashboard.

Os tooltips dos tiles e as tabelas da pagina Definicoes saem daqui, para nunca
divergirem. So importa pandas: sem streamlit o modulo e testavel sem subir app.
"""

import pandas as pd

# Ordem de leitura das paginas 1 a 4. `nome` e o titulo literal do tile; quando o
# titulo e montado por f-string, `ancora` guarda o trecho estavel que o teste procura
# no arquivo da pagina.
KPIS = (
    {
        "slug": "faturamento_total",
        "pagina": "Visão Geral",
        "arquivo": "Home.py",
        "nome": "Faturamento Total",
        "ancora": None,
        "view": "vw_kpis_mensais",
        "definicao": (
            "Soma do valor das vendas concretizadas (Entregue e Enviado) no recorte. "
            "O delta compara com a janela anterior de mesmo tamanho."
        ),
    },
    {
        "slug": "ticket_medio",
        "pagina": "Visão Geral",
        "arquivo": "Home.py",
        "nome": "Ticket Médio",
        "ancora": None,
        "view": "vw_kpis_mensais",
        "definicao": (
            "Faturamento dividido pelo número de pedidos do recorte, "
            "não por item nem por cliente."
        ),
    },
    {
        "slug": "taxa_retencao",
        "pagina": "Visão Geral",
        "arquivo": "Home.py",
        "nome": "Taxa de Retenção",
        "ancora": None,
        "view": "vw_kpis_mensais",
        "definicao": (
            "Média mensal, nos meses do recorte, do percentual de clientes do mês "
            "anterior que voltaram a comprar."
        ),
    },
    {
        "slug": "churn_rate",
        "pagina": "Visão Geral",
        "arquivo": "Home.py",
        "nome": "Churn Rate",
        "ancora": None,
        "view": "vw_kpis_mensais",
        "definicao": (
            "Percentual de clientes sem compra há 90 dias. A janela saiu do percentil "
            "90 real entre recompras, 101 dias, arredondado para mês cheio."
        ),
    },
    {
        "slug": "clientes_ativos",
        "pagina": "Clientes",
        "arquivo": "pages/2_Clientes.py",
        "nome": "Clientes Ativos (média mensal)",
        "ancora": None,
        "view": "vw_kpis_mensais",
        "definicao": (
            "Média, nos meses do recorte, do número de clientes distintos com ao menos "
            "uma compra concretizada no mês."
        ),
    },
    {
        "slug": "clientes_novos",
        "pagina": "Clientes",
        "arquivo": "pages/2_Clientes.py",
        "nome": "Novos no Período",
        "ancora": None,
        "view": "vw_kpis_mensais",
        "definicao": (
            "Soma dos clientes cuja primeira compra da base inteira caiu dentro do "
            "recorte selecionado."
        ),
    },
    {
        "slug": "ticket_medio_cliente",
        "pagina": "Clientes",
        "arquivo": "pages/2_Clientes.py",
        "nome": "Ticket Médio por Cliente",
        "ancora": None,
        "view": "vw_kpis_mensais",
        "definicao": (
            "Faturamento do recorte dividido pela soma de clientes ativos mês a mês. "
            "Difere do ticket por pedido da Visão Geral."
        ),
    },
    {
        "slug": "receita_top10",
        "pagina": "Clientes",
        "arquivo": "pages/2_Clientes.py",
        "nome": "Receita no Top 10% de clientes",
        "ancora": None,
        "view": "vw_receita_top_clientes",
        "definicao": (
            "Percentual da receita concentrado nos 10% maiores clientes. Calculado "
            "sobre a base completa; não reage aos filtros."
        ),
    },
    {
        "slug": "skus_ativos",
        "pagina": "Produtos",
        "arquivo": "pages/3_Produtos.py",
        "nome": "SKUs ativos no recorte",
        "ancora": None,
        "view": "vw_vendas",
        "definicao": (
            "Produtos distintos com ao menos uma venda concretizada dentro do recorte "
            "selecionado."
        ),
    },
    {
        "slug": "categoria_lider",
        "pagina": "Produtos",
        "arquivo": "pages/3_Produtos.py",
        "nome": "Categoria líder no recorte",
        "ancora": None,
        "view": "vw_vendas",
        "definicao": (
            "Categoria de maior faturamento dentro do recorte atual. Muda conforme os "
            "filtros da barra lateral."
        ),
    },
    {
        "slug": "produto_lider",
        "pagina": "Produtos",
        "arquivo": "pages/3_Produtos.py",
        "nome": "Produto líder (base completa)",
        "ancora": None,
        "view": "vw_pareto_produtos",
        "definicao": (
            "SKU de maior faturamento na base inteira, primeira posição do Pareto. "
            "Não reage aos filtros."
        ),
    },
    {
        "slug": "concentracao_top20",
        "pagina": "Produtos",
        "arquivo": "pages/3_Produtos.py",
        "nome": "Concentração: top 20% dos produtos",
        "ancora": "Concentração: top 20% dos produtos",
        "view": "vw_pareto_produtos",
        "definicao": (
            "Percentual do faturamento acumulado nos 20% primeiros produtos do Pareto. "
            "Sempre sobre a base completa, ao contrário dos dois indicadores à "
            "esquerda, que respeitam o recorte."
        ),
    },
    {
        "slug": "previsao_proximo_mes",
        "pagina": "Previsão",
        "arquivo": "pages/4_Previsão.py",
        "nome": "Previsão para o próximo mês",
        "ancora": "Previsão para ",
        "view": "vw_previsao",
        "definicao": (
            "Estimativa pontual da regressão para o primeiro mês fora da base, com a "
            "banda logo abaixo desta linha. Ordem de grandeza para planejamento, "
            "não meta."
        ),
    },
    {
        "slug": "mae_regressao",
        "pagina": "Previsão",
        "arquivo": "pages/4_Previsão.py",
        "nome": "MAE da regressão (teste)",
        "ancora": None,
        "view": "vw_metricas_modelo",
        "definicao": (
            "Erro absoluto médio, em reais, nos 6 meses de teste (jan-jun/2026), "
            "medidos fora do treino."
        ),
    },
    {
        "slug": "mape_regressao",
        "pagina": "Previsão",
        "arquivo": "pages/4_Previsão.py",
        "nome": "MAPE da regressão (teste)",
        "ancora": None,
        "view": "vw_metricas_modelo",
        "definicao": (
            "O mesmo erro em percentual do realizado, o que permite comparar séries de "
            "escala diferente."
        ),
    },
    {
        "slug": "r2_regressao",
        "pagina": "Previsão",
        "arquivo": "pages/4_Previsão.py",
        "nome": "R2 da regressão (teste)",
        "ancora": None,
        "view": "vw_metricas_modelo",
        "definicao": (
            "Fração da variância explicada pelo modelo no teste. Negativo significa "
            "desempenho pior do que prever sempre a média."
        ),
    },
)

POR_SLUG = {k["slug"]: k for k in KPIS}


def ajuda(slug: str) -> str:
    """Texto do tooltip de um tile. Slug inexistente estoura, e o smoke pega."""
    kpi = POR_SLUG[slug]
    return f"{kpi['definicao']} Fonte: view {kpi['view']}."


def tabela_kpis() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "KPI": [k["nome"] for k in KPIS],
            "Definição": [k["definicao"] for k in KPIS],
            "View": [k["view"] for k in KPIS],
            "Página": [k["pagina"] for k in KPIS],
        }
    )


# Mesma ordem do CASE em sql/views/006_vw_rfm.sql, e os nomes batem caractere a
# caractere com as strings do THEN - acento errado nao estoura, so mente na tabela.
SEGMENTOS = (
    {
        "segmento": "Campeões",
        "regra": "R >= 4 e F >= 4",
        "acao": "Proteger. É o grupo que mais concentra receita, e qualquer atrito custa caro.",
    },
    {
        "segmento": "Potenciais leais",
        "regra": "R >= 4 e F >= 2",
        "acao": "Aumentar a frequência com recomendação e recompra programada.",
    },
    {
        "segmento": "Novos",
        "regra": "R >= 4",
        "acao": "Garantir a segunda compra, que é onde a curva de retenção mais cai.",
    },
    {
        "segmento": "Leais",
        "regra": "R = 3 e F >= 4",
        "acao": "Reconhecer e manter. Compram sempre, mas não compraram tão recentemente.",
    },
    {
        "segmento": "Precisam de atenção",
        "regra": "R = 3 e F >= 2",
        "acao": "Lembrete de recompra antes que a recência avance mais.",
    },
    {
        "segmento": "Promissores",
        "regra": "R = 3",
        "acao": "Testar oferta de entrada e observar se a frequência sobe.",
    },
    {
        "segmento": "Não pode perder",
        "regra": "F >= 4",
        "acao": "Contato direto. Compravam muito e pararam, então a perda é grande.",
    },
    {
        "segmento": "Em Risco",
        "regra": "F >= 2",
        "acao": "Campanha de reativação. Valor comprovado e relação ainda morna.",
    },
    {
        "segmento": "Prestes a dormir",
        "regra": "R = 2",
        "acao": "Reativação barata, por e-mail ou cupom, antes de virar perda.",
    },
    {
        "segmento": "Perdidos",
        "regra": "qualquer outro caso",
        "acao": "Entender o motivo da perda vale mais do que insistir na reativação.",
    },
)


def tabela_segmentos() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Segmento": [s["segmento"] for s in SEGMENTOS],
            "Regra (score R e F)": [s["regra"] for s in SEGMENTOS],
            "Ação sugerida": [s["acao"] for s in SEGMENTOS],
        }
    )


LIMITACOES = (
    "Os dados são sintéticos, gerados por script com seed fixa. Os padrões são "
    "plausíveis e reprodutíveis, mas não descrevem nenhuma empresa real.",
    "A base é um snapshot congelado em jun/2026. A recência do RFM e os presets de "
    "período contam a partir da última venda da base, não do relógio.",
    "São 24 meses de histórico, ou seja, 24 observações mensais e apenas dois "
    "novembros. É pouco para estimar sazonalidade com segurança.",
    "O R2 no teste é negativo nos dois modelos, regressão e baseline. A previsão vale "
    "como ordem de grandeza para planejamento, não como meta.",
)
