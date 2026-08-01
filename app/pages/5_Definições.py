"""Pagina 5 - Definicoes e metodo."""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="InsightFlow - Definições", layout="wide")

# Sem theme e sem ui, ao contrario das outras quatro paginas: theme existe para
# registrar o template do Plotly, e aqui nao ha grafico nenhum.
import definicoes
import filtros

st.title("Definições e método")

# Sidebar desenhada mas nao aplicada, igual a Previsao: o Streamlit descarta estado
# de widget que nao foi renderizado, entao e isto que preserva o recorte na navegacao.
op = filtros.opcoes()
filtros.sidebar(op)

st.markdown(
    "A base cobre 24 meses, de jul/2024 a jun/2026. É sintética, gerada por script "
    "com seed fixa, e o CSV bruto está commitado no repositório.\n\n"
    "Venda concretizada é o pedido com status Entregue ou Enviado. Cancelado e "
    "Devolvido não são receita; Processando fica de fora por conservadorismo, porque "
    "ainda pode virar cancelamento.\n\n"
    "Os filtros da barra lateral são globais, mas as análises estruturais (RFM, "
    "coorte, Pareto, métricas por produto, share do top 10%) não reagem a eles. "
    "Esta página também não."
)

# Medida de leitura: em largura total a coluna de definicao passa de 1400px, larga
# demais para ler. Nao e mudanca de layout do dashboard, e tipografia.
col, _ = st.columns([3, 1])

with col:
    st.subheader("Indicadores")
    st.table(definicoes.tabela_kpis(), hide_index=True)

    st.subheader("Segmentos RFM")
    st.caption(
        "As dez regras são avaliadas na ordem desta tabela e a primeira que casa "
        "vence. Juntas cobrem os 25 pares de score R e F sem sobra nem sobreposição."
    )
    st.table(definicoes.tabela_segmentos(), hide_index=True)

st.subheader("Limitações conhecidas")
st.markdown("\n".join(f"- {limitacao}" for limitacao in definicoes.LIMITACOES))
