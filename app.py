import streamlit as st
import pandas as pd

# Configuração inicial da Página
st.set_page_config(page_title="Monitor de Jogos", layout="wide")

st.title("🎲 Monitor de Preços de Jogos de Tabuleiro")

# Carregar os Dados
try:
    # Lê o arquivo csv gerado
    df = pd.read_csv("games_data.csv")

    col1, col2 = st.columns(2)
    # Tamanho total do dataframe
    col1.metric("Total de Ofertas", len(df))
    # Quantidade de itens únicos em "jogo"
    col2.metric("Jogos Monitorados", df["jogo"].nunique())

    opcoes_jogos = df["jogo"].unique()

    # O multiselect permite escolher vários jogos
    jogos_selecionados = st.sidebar.multiselect(
        "Selecione os Jogos:",
        options=opcoes_jogos,
        default=opcoes_jogos # Por padrão, vem todos selecionados
    )

    # --- Lógica de Filtragem ---
    if jogos_selecionados:
        # Filtra o DF deixando só os jogos selecionados
        df_filtrado = df[df["jogo"].isin(jogos_selecionados)]
    else:
        # Se o usuário tirar tudo, fica vazio
        df_filtrado = df
    
    # Mostra dados simples (reagentes ao filtro)
    col1, col2, col3 = st.columns(3)
    # Tamanho total do dataframe filtrado
    col1.metric("Total de Ofertas", len(df_filtrado))
    # Quantidade de itens únicos em "jogo"
    col2.metric("Jogos Listados", df_filtrado["jogo"].nunique())

    # Preço Médio
    # Convertendo a coluna 'preco' (de texto 'R$...') para real
    try:
        # Limpeza rápida: tira R$, troca virgula por ponto
        media_preco = df_filtrado["preco"].str.replace("R$", "").str.replace(".", "").str.replace(",", ".").astype(float).mean()
        col3.metric("Preço Médio", f"R$ {media_preco:.2f}")
    except:
        col3.metric("Preço Médio", "N/A")

    st.markdown("---") # Divisória em markdown

    st.subheader("📋 Lista de Ofertas")
    
    # Tabela filtrada
    st.dataframe(
        df_filtrado, 
        use_container_width=True,
        hide_index=True # Esconder a coluna de números 0,1,2,3...
    )

# Se não carregar os dados, tem alguma coisa muito errada
except FileNotFoundError:
    st.error("Arquivo 'games_data.csv' não encontrado. Rode o scraper primeiro!")