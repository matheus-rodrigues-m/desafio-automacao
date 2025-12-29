import streamlit as st
import pandas as pd

# Configuração inicial da Página
st.set_page_config(page_title="Monitor de Jogos", layout="wide")

st.title("🎲 Monitor de Preços de Jogos de Tabuleiro")

# Carregar os Dados
try:
    # Lê o arquivo csv gerado
    df = pd.read_csv("games_data.csv")

    # Já criar uma nova coluna 'preco_num' convertendo texto 'R$ 99,90' pra float 99.90
    # Tirando o R%, substituindo a , por .
    df["preco_num"] = df["preco"].apply(lambda x: 
                                        float(x.replace("R$", "")
                                              .replace(".", "")
                                              .replace(",", ".").strip()))
    
    # --- SIDEBAR ---
    # multiselect para escolher vários jogos
    st.sidebar.header("🔍 Filtros")
    opcoes_jogos = df["jogo"].unique()
    jogos_selecionados = st.sidebar.multiselect(
        "Selecione os Jogos:",
        options=opcoes_jogos,
        default=opcoes_jogos
    )

    st.subheader("🎲 Dados Gerais:")

    col1, col2 = st.columns(2)
    # Tamanho total do dataframe
    col1.metric("Total de Ofertas", len(df))
    # Quantidade de itens únicos em "jogo"
    col2.metric("Jogos Monitorados", df["jogo"].nunique())

    opcoes_jogos = df["jogo"].unique()

    # --- Lógica de Filtragem ---
    if jogos_selecionados:
        # Filtra o DF deixando só os jogos selecionados
        df_filtrado = df[df["jogo"].isin(jogos_selecionados)]
    else:
        # Se o usuário tirar tudo, ficaria vazio
        # Mas colocamos default com tudo selecionado :)
        df_filtrado = df
    
    st.subheader("📊 Dados Filtrados:")

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
        # Isso aqui já foi feito mais cedo
        # media_preco = df_filtrado["preco"].str.replace("R$", "").str.replace(".", "").str.replace(",", ".").astype(float).mean()
        media_preco = df_filtrado["preco_num"].mean()
        col3.metric("Preço Médio", f"R$ {media_preco:.2f}")
    except:
        col3.metric("Preço Médio", "N/A")

    st.markdown("---") # Divisória em markdown

    # --- Gráfico comparativo de preços por loja ---
    # Aqui a gente descobre qual é a mais cara e a mais barata
    st.subheader("📊 Comparativo de Preços")

    # Gráfico de barras usando a coluna numérica de preços (df["preco_num"])
    st.bar_chart(
        df_filtrado,
        x="loja",
        y="preco_num",
        color="jogo",
        stack=False 
    )

    # --- TABELA ---
    st.subheader("📋 Detalhes das Ofertas")
    st.dataframe(
        # Mostra só as colunas originais (esconde o preco_num)
        df_filtrado[["jogo", "loja", "preco", "link"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "link": st.column_config.LinkColumn("Link da Oferta") # Deixa o link clicável
        }
    )

# Se não carregar os dados, tem alguma coisa muito errada
except FileNotFoundError:
    st.error("Arquivo 'games_data.csv' não encontrado. Rode o scraper primeiro!")