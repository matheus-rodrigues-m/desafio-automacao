import streamlit as st
import pandas as pd

# Configuração inicial da Página
st.set_page_config(page_title="Monitor de Jogos", layout="wide")

st.title("🎲 Monitor de Preços de Jogos de Tabuleiro")


# --- Função de Limpeza Mais Robusta ---
def converter_preco(valor):
    """Converte 'R$ 99,90' para float 99.90. Se falhar, retorna None."""
    try:
        if isinstance(valor, str):
            # Remove R$, troca ponto por nada (milhar) e vírgula por ponto (decimal)
            valor_limpo = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(valor_limpo)
        return float(valor)
    except:
        return None # Retorna vazio se der erro (ex: "Esgotado")

# Carregar os Dados
try:
    # Lê o arquivo csv gerado
    df = pd.read_csv("games_data.csv")

    # Aplica a conversão / limpeza mais robusta
    df["preco_num"] = df["preco"].apply(converter_preco)

    # Remove linhas onde o preço não foi identificado (None) para não sujar o gráfico
    df = df.dropna(subset=["preco_num"])

    # Já criar uma nova coluna 'preco_num' convertendo texto 'R$ 99,90' pra float 99.90
    # Tirando o R%, substituindo a , por : -SUBSTITUÍDO PELA FUNÇÃO converter_preco-
    # df["preco_num"] = df["preco"].apply(lambda x: float(x.replace("R$", "").replace(".", "").replace(",", ".").strip()))
    
    # --- SIDEBAR ---
    # multiselect ora escolher vários jogos
    st.sidebar.header("🔍 Filtros")

    # Filtro de Jogos
    opcoes_jogos = df["jogo"].unique()
    jogos_selecionados = st.sidebar.multiselect(
        "Selecione os Jogos:",
        options=opcoes_jogos,
        default=opcoes_jogos # Tudo marcado por padrão
    )

    # Filtro de Lojas
    opcoes_lojas = df["loja"].unique()
    lojas_selecionadas = st.sidebar.multiselect(
        "Selecione as Lojas:",
        options=opcoes_lojas,
        default=opcoes_lojas # Tudo marcado por padrão
    )

    st.subheader("🎲 Dados Gerais:")

    col1, col2, col3, col4 = st.columns(4)
    # Tamanho total do dataframe
    col1.metric("Total de Ofertas", len(df))
    # Quantidade de itens únicos em "jogo"
    col2.metric("Jogos Monitorados", df["jogo"].nunique())
    # Quantidade de itens únicos em "loja"
    col3.metric("Lojas Listadas", df["loja"].nunique())
    # Média dos preços gerais
    media_preco = df["preco_num"].mean()
    col4.metric("Preço Médio", f"R$ {media_preco:.2f}")

    opcoes_jogos = df["jogo"].unique()

    # Começar considerando o DF todo
    df_filtrado = df.copy()

    # --- Lógica de Filtragem ---
    if jogos_selecionados:
        # Filtra o DF deixando só os jogos selecionados
        df_filtrado = df_filtrado[df_filtrado["jogo"].isin(jogos_selecionados)]

    if lojas_selecionadas:
        df_filtrado = df_filtrado[df_filtrado["loja"].isin(lojas_selecionadas)]
    
    st.subheader("📊 Dados Filtrados:")

    col1, col2, col3, col4 = st.columns(4)
    # Tamanho total do dataframe filtrado
    col1.metric("Total de Ofertas", len(df_filtrado))
    # Quantidade de itens únicos em "jogo"
    col2.metric("Jogos Listados", df_filtrado["jogo"].nunique())
    # Quantidade de itens únicos em "loja"
    col3.metric("Lojas Listadas", df_filtrado["loja"].nunique())

    # Preço Médio
    # pega a média da coluna preço_num e coloca formatado em reais    
    if not df_filtrado.empty:
        media_preco = df_filtrado["preco_num"].mean()
        col4.metric("Preço Médio", f"R$ {media_preco:.2f}")
    else:
        col4.metric("Preço Médio", "R$ 0,00")
    

    st.markdown("---") # Divisória em markdown

    # --- Gráfico comparativo de preços por loja ---
    # Aqui a gente descobre qual é a mais cara e a mais barata
    st.subheader("📊 Comparativo de Preços")

    if not df_filtrado.empty:
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
except Exception as e:
    st.error(f"❌ Erro inesperado: {e}")