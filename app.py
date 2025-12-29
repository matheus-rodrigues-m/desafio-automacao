import streamlit as st
import pandas as pd

# Configuração inicial da Página
st.set_page_config(page_title="Monitor de Jogos", layout="wide")

st.title("🎲 Monitor de Preços de Jogos de Tabuleiro")

# Carregar os Dados
try:
    # Lê o arquivo csv gerado
    df = pd.read_csv("games_data.csv")
    
    # Mostra dados simples (só pra testar)
    col1, col2 = st.columns(2)
    # Tamanho total do dataframe
    col1.metric("Total de Ofertas", len(df))
    # Quantidade de itens únicos em "jogo"
    col2.metric("Jogos Monitorados", df["jogo"].nunique())

    # Exibe tabela com os dados
    st.subheader("📋 Dados Coletados")
    st.dataframe(df, use_container_width=True)

# Se não carregar os dados, tem alguma coisa muito errada
except FileNotFoundError:
    st.error("Arquivo 'games_data.csv' não encontrado. Rode o scraper primeiro!")