######## IMPORTAÇÕES NECESSÁRIAS
import json
import pandas as pd
import yaml
import requests
import os
from tqdm import tqdm
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from transformers import pipeline

######## DEFININDO VARIÁVEIS GLOBAIS OU QUE SERÃO USADAS COM FREQUÊNCIA
load_dotenv()
CAMARA_BASE_URL = 'https://dadosabertos.camara.leg.br/api/v2/'
# GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
# model = genai.GenerativeModel("gemini-1.5-flash")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
with open('../data/config.yaml', 'r', encoding='utf-8') as file:
    CAMARA_SUMMARY = yaml.safe_load(file)

dt_inicio = "2024-08-01"
dt_fim = "2024-08-30"

#================================== EXERCÍCIO 3 ==================================#
# #=======================================#=======================================

######## COLETA DE DADOS DOS DEPUTADOS
def request_api_camara() -> pd.DataFrame:
    url = f'{CAMARA_BASE_URL}/deputados'
    response = requests.get(url)
    if not response.ok:
        raise Exception('Nao foi possivel recuperar os dados')
    df_deputados = pd.DataFrame().from_dict(json.loads(response.text)['dados'])
    return df_deputados


######## SALVAR OS DADOS EM ARQUIVO PARQUET
def create_file_deputados_parquet(df: pd.DataFrame, path: str):
    df.to_parquet(f"{path}")


df_deputados = request_api_camara()
# create_file_deputados_parquet(df_deputados, 'deputados.parquet')


######## PROMPT PARA O CÓDIGO QUE GERA UM GRÁFICO EM PIZZA
def pizza_chart_code() -> str:
    data_deputados_parquet = pd.read_parquet("../data/deputados.parquet")
    system_prompt = f"""
        You are an AI assistant specialized in python code and data analysis.
        You will receive a .parquet file {data_deputados_parquet} from '../data/deputados.parquet'
        Your job is to build a python code to generate a pizza chart with the total and the percentual of 'deputados' from each 'partido'. Save the pizza chart in '../docs/distribuicao_deputados.png'.

        Important observations:
        -There is no need to explain the code.
        -pandas has already been imported as 'pd'.

        Make it easy to understand the chart, with labels, titles and different colors for 'partido'.
    """
    response = llm.invoke(system_prompt)
    return response.content


# chart_code = pizza_chart_code()
# analysis_code = chart_code.replace("```python\n",'').replace("\n```",'')
# # exec(analysis_code)


######## PROMPT PARA A ANÁLISE E INSIGHTS DOS DEPUTADOS
def data_analysis_pizza_chart():
    party_distribution = f"""
        PL: 18.1%
        PT: 13.3%
        UNIAO: 11.5%
        PP: 9.7%
        PSD: 8.6%
        REPUBLICANOS: 8.6%
        MDB: 8.6%
        ... (other parties and its distribution)
    """
    system_prompt = f"""
        You are a senior political analyst with extensive experience in Brazilian legislative politics.
        You have a previous knowledge about 'Câmara dos Deputados' provided by {CAMARA_SUMMARY['overview_summary']}.

        Here is the party distribution:
        {party_distribution}

        Analyse what this distribution of 'deputados' says about the total and the percentual of 'deputados' from each 'partido'. Your job is to generate insights about the distribution of 'partidos' and how this affects 'Câmara dos Deputados'.

        ## EXAMPLE
        PT: 15%
        If the 'partido' PT has a big percentage in 'Câmara dos Deputados' it will probably be less severe with the actions of the current president.

        Please provide your analysis in clear, concise terms, supporting your conclusions with specific numbers from the party distribution data.

        Give the anwser in a json format.
    """

    response = llm.invoke(system_prompt)
    return response.content

file_path_distribuicao = '../data/insights_distribuicao_deputados.json'
if not os.path.exists(file_path_distribuicao):
    insights_distribuicao_deputados = data_analysis_pizza_chart()
    json_insights_code = json.loads(insights_distribuicao_deputados.replace("```json\n",'').replace("\n```",''))
    with open(file_path_distribuicao, 'w', encoding='utf-8') as f:
        json.dump(json_insights_code, f, ensure_ascii=False, indent=4)

#================================================================================#
# #=======================================#=======================================


#================================== EXERCÍCIO 4 ==================================#
# #=======================================#=======================================

def despesas_deputados_api_camara() -> pd.DataFrame:
    list_expenses = []
    for id in tqdm(df_deputados.id.unique()):
        url = f'{CAMARA_BASE_URL}/deputados/{id}/despesas'
        params = {
            'ano': 2024,
            'mes': 8,
            'itens': 100,
        }
        response = requests.get(url, params)
        df_resp = pd.DataFrame().from_dict(json.loads(response.text)['dados'])
        df_resp['id'] = id
        list_expenses.append(df_resp)

    df_despesas_deputados = pd.concat(list_expenses)
    
    return df_despesas_deputados


file_path_despesas = "../data/serie_despesas_diarias_deputados.parquet"
if not os.path.exists(file_path_despesas):
    df_data_despesa = despesas_deputados_api_camara()
    filtered_data_depesas_deputados = df_data_despesa[["id","dataDocumento","ano", "mes", "tipoDespesa", "valorLiquido"]]
    df_expense = filtered_data_depesas_deputados.merge(df_deputados, on=['id'])
    create_file_deputados_parquet(df_expense, file_path_despesas)

if os.path.exists(file_path_despesas):
    data_depesas_deputados_parquet = pd.read_parquet(file_path_despesas)

def prompt_chaining(df: pd.DataFrame):
    prompt_start = f"""
        You are a data scientist specialized in analysing political content. You are working on the 'Câmara dos Deputados', investigating patterns in a .parquet file {df} from '../data/serie_despesas_diarias_deputados.parquet', what shows the expenses of each 'deputado'.

        That's the collumns we have:
        - id: "deputado's" identifier
        - dataDocumento: datatime of when the expense happened
        - ano: year
        - mes: month
        - tipoDespesa: Type of the expense
        - valorLiquido: Value of the expense

        Generate a list of 3 analyses that can be implemented given the available {df}, as a JSON file:
        {[
            {'Name':'analysis name',
            'Objective': 'what we need to analyze',
            'Method': 'how we analyze it'
            }
        ]
        }
    """
    response = llm.invoke(prompt_start)
    return response.content

response_prompt_start_chaining = prompt_chaining(data_depesas_deputados_parquet)
prompt_start_chaining = json.loads(response_prompt_start_chaining.replace("```json\n",'').replace("\n```",''))
# print(prompt_start_chaining)


def prompt_analysis_chaining(resp: json, df: pd.DataFrame) -> list:
    response_list = []
    for i in range(len(resp)):
        prompt_analysis = f"""
            You are a data scientist specialized in analysing political content. You are working on the 'Câmara dos Deputados', investigating patterns in a .parquet file {df} from '../data/serie_despesas_diarias_deputados.parquet', what shows the expenses of each 'deputado'.

            That's the collumns we have:
            - id: "deputado's" identifier
            - dataDocumento: datatime of when the expense happened
            - ano: year
            - mes: month
            - tipoDespesa: Type of the expense
            - valorLiquido: Value of the expense

            Implement the analysis described below in python.
            Output only the code, no need to explanations.
            ## ANALYSIS
            {resp[i]}
        """ 
        response = llm.invoke(prompt_analysis)
        response_list.append(response.content)
    return response_list


# print("")
# print("")
resp_list_analysis = prompt_analysis_chaining(prompt_start_chaining, data_depesas_deputados_parquet)


def prompt_generated_knowledge(data: list, df: pd.DataFrame):
    for obj in data:
        repl_obj = obj.replace("```python\n",'').replace("\n```",'')
        prompt = f"""
            You are a data scientist specialized in analysing political content. You are working on the 'Câmara dos Deputados', investigating patterns.
            Your job is to generate insights from the given data and the analysis.

            ## DATA
            {df}

            ## ANALYSIS
            {repl_obj}

            ## INSIGHTS
            ...

            Please provide your analysis in clear, concise terms, supporting your conclusions with specific numbers from the data.
            Give the anwser in a json format.

            {[
            {'Title':'insight name',
            'Insight': 'insight',
            }
             ]
            }
        """
        response = llm.invoke(prompt)
        return response.content
    

file_path_despesas_insights = '../data/insights_despesas_deputados.json'
if not os.path.exists(file_path_despesas_insights):
    insights_deputados_expenses = prompt_generated_knowledge(resp_list_analysis, data_depesas_deputados_parquet)
    json_insights_code_expenses = json.loads(insights_deputados_expenses.replace("```json\n",'').replace("\n```",''))
    with open(file_path_despesas_insights, 'w', encoding='utf-8') as f:
        json.dump(json_insights_code_expenses, f, ensure_ascii=False, indent=4)

#================================================================================#
# #=======================================#=======================================


#================================== EXERCÍCIO 5 ==================================#
# #=======================================#=======================================


## As ementas das proposições, na maioria, não possuem texto o suficiente para fazer uma sumarização por chunks...

def prop() -> pd.DataFrame:
    list_prop = []
    list_aux = []

    pd.set_option('display.max_colwidth', None)

    url = f'{CAMARA_BASE_URL}/proposicoes'
    params = {
        'dataInicio': dt_inicio,
        'dataFim': dt_fim,
        'itens': 100,
    }
    # Execucao da primeira pagina de resultados.
    response = requests.get(url, params)
    df_r = pd.DataFrame().from_dict(json.loads(response.text)['dados'])
    # Link para proxima pagina
    df_links = pd.DataFrame().from_dict(json.loads(response.text)['links'])
    df_links = df_links.set_index('rel').href
    list_aux.append(df_r)

    # print(df_r.id.unique())

    aux = 3
    while aux > 0:
        response = requests.get(df_links['next'])
        df_r = pd.DataFrame().from_dict(json.loads(response.text)['dados'])
        list_aux.append(df_r)
        # Link para proxima pagina
        df_links = pd.DataFrame().from_dict(json.loads(response.text)['links'])
        df_links = df_links.set_index('rel').href
        aux -= 1

    df_r = pd.concat(list_aux, ignore_index=True)

    for id in tqdm(df_r.id.unique()):
        resp = requests.get(f'{CAMARA_BASE_URL}/proposicoes/{id}/temas')
        df_resp = pd.DataFrame().from_dict(json.loads(resp.text)['dados'])
        df_resp['id'] = id
        list_prop.append(df_resp)
        # print(f"Appended DataFrame for id {id}:")
    
    # print(len(list_prop))

    df_temas_proposicoes = pd.concat(list_prop, ignore_index=True)

    df_proposicoes = df_r.merge(df_temas_proposicoes, on='id', suffixes=('', '_drop'))
    df_proposicoes.drop([col for col in df_proposicoes.columns if 'drop' in col], axis=1, inplace=True)

    filter = ['Economia', 'Educação', 'Ciência, Tecnologia e Inovação']

    df_proposicoes_filtered = df_proposicoes[df_proposicoes['tema'].isin(filter)]

    df_proposicoes_filtered_counter = df_proposicoes_filtered.groupby('tema').head(10)

    return df_proposicoes_filtered_counter


file_path_proposicoes = "../data/proposicoes_deputados.parquet"
if not os.path.exists(file_path_proposicoes):
    proposicoes = prop()
    create_file_deputados_parquet(proposicoes, file_path_proposicoes)


if os.path.exists(file_path_proposicoes):
    data_proposicoes_parquet = pd.read_parquet(file_path_proposicoes).reset_index(drop=True)


# def split_into_chunks(text, max_length=500):
#     words = text.split()
#     chunks = []
#     for i in range(0, len(words), max_length):
#         chunk = " ".join(words[i:i+max_length])
#         chunks.append(chunk)
#     return chunks


# def summarize_text_by_chunks(text, max_length=500):
#     chunks = split_into_chunks(text, max_length)
#     summarized_chunks = [summarizer(chunk, max_length=50, min_length=10, do_sample=False)[0]['summary_text'] for chunk in chunks]
#     return " ".join(summarized_chunks)


# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
# print(summarizer)

# data_proposicoes_parquet['resumo'] = data_proposicoes_parquet['ementa'].apply(summarize_text_by_chunks)
# output_path = "../data/sumarizacao_proposicoes.json"
# os.makedirs(os.path.dirname(output_path), exist_ok=True)

# data_proposicoes_parquet.to_json(output_path, orient="records", lines=False, indent=4, force_ascii=False)
#================================================================================#
# #=======================================#======================================= 