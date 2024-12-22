import streamlit as st
import pandas as pd
import yaml
from PIL import Image
import json

# Configurações iniciais
st.set_page_config(page_title="Dashboard", layout="wide")

# Barra lateral para navegação
st.sidebar.title("Menu")
aba = st.sidebar.radio("Selecione a aba:", ["Overview", "Despesas", "Proposições"])

# Aba Overview
if aba == "Overview":
    #================================== EXERCÍCIO 6 ==================================#
    # #=======================================#=======================================
    st.title("Overview")
    st.write("Bem-vindo ao painel de visão geral.")
    
    # Carregar o arquivo config.yaml
    try:
        with open('../data/config.yaml', 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
            overview_summary = config_data.get('overview_summary', 'Nenhum resumo disponível.')
            st.subheader("Resumo")
            st.write(overview_summary)
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo config.yaml: {e}")
    
    # Carregar o gráfico de barras
    try:
        image_path = '../docs/distribuicao_deputados.png'
        image = Image.open(image_path)
        st.subheader("Distribuição de Deputados")
        st.image(image, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar o gráfico de barras: {e}")


    # Carregar os insights do LLM sobre a distribuição de deputados
    try:
        with open('../data/insights_distribuicao_deputados.json', 'r', encoding='utf-8') as file:
            insights_data = json.load(file)
            st.subheader("Insights sobre a Distribuição de Deputados")
            st.write(f"Overall Distribution: {insights_data['analysis']['overall_distribution']}")
            for insight in insights_data['analysis'].get('major_parties_influence', []):
                st.json(f"{insight}")
            st.write(f"Implications for Camara")
            for insight in insights_data['analysis'].get('implications_for_camara', []):
                st.json(f"{insight}")
    except Exception as e:
        st.error(f"Erro ao carregar os insights sobre a distribuição de deputados: {e}")

    #================================================================================#
    # #=======================================#======================================= 

# Aba Despesas
    #================================== EXERCÍCIO 7 ==================================#
    # #=======================================#=======================================
elif aba == "Despesas":
    st.title("Despesas")
    st.write("Nesta seção, você pode visualizar e analisar as despesas dos deputados.")
    
    # Carregar insights sobre despesas
    try:
        with open('../data/insights_despesas_deputados.json', 'r', encoding='utf-8') as file:
            insights_despesas = json.load(file)
            st.subheader("Insights sobre Despesas dos Deputados")
            for dict in insights_despesas:
                st.json(f"{dict}", expanded=False)
    except Exception as e:
        st.error(f"Erro ao carregar os insights sobre despesas: {e}")
    
    # Carregar série de despesas e criar selectbox
    try:
        despesas_df = pd.read_parquet('../data/serie_despesas_diarias_deputados.parquet')
        deputados = despesas_df['nome'].unique()
        deputado_selecionado = st.selectbox("Selecione o deputado:", options=deputados)
        
        # Filtrar dados do deputado selecionado
        despesas_deputado = despesas_df[despesas_df['nome'] == deputado_selecionado]
        
        # Mostrar gráfico de barras com a série temporal
        st.subheader(f"Série Temporal de Despesas - {deputado_selecionado}")
        st.write("Período: 08/2024")
        if not despesas_deputado.empty:
            chart = despesas_deputado.groupby('tipoDespesa')['valorLiquido'].sum().reset_index()
            st.bar_chart(chart.set_index('tipoDespesa')['valorLiquido'])
        else:
            st.write("Não há dados disponíveis para o deputado selecionado.")
    except Exception as e:
        st.error(f"Erro ao carregar ou processar os dados de despesas: {e}")

# Aba Proposições
elif aba == "Proposições":
    st.title("Proposições")
    st.write("Nesta seção, você pode explorar proposições ou ações relacionadas.")
    # Mostrar tabela de proposições
    try:
        proposicoes_df = pd.read_parquet('../data/proposicoes_deputados.parquet').reset_index(drop=True)
        st.subheader("Tabela de Proposições")
        st.dataframe(proposicoes_df)
    except Exception as e:
        st.error(f"Erro ao carregar os dados de proposições: {e}")
    
    # Mostrar resumo das proposições
    try:
        with open('../data/sumarizacao_proposicoes.json', 'r', encoding='utf-8') as file:
            resumo_proposicoes = json.load(file)
            st.subheader("Resumo das Proposições")
            for resumo in resumo_proposicoes:
                st.write(f"- {resumo['resumo']}")
    except Exception as e:
        st.error(f"Erro ao carregar o resumo das proposições: {e}")