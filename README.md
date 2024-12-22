# Câmara dos Deputados Data Analysis App

## Visão Geral
O Câmara dos Deputados Data Analysis App é uma aplicação interativa para análise de dados da Câmara dos Deputados, permitindo que os usuários explorem informações detalhadas sobre deputados, despesas e proposições. A aplicação combina processamento de dados, visualização interativa e inteligência artificial para gerar insights valiosos diretamente a partir dos dados disponibilizados pela API da Câmara dos Deputados.

## Features
- **Frameworks**: Streamlit, Torch, Transformers, Pandas.
- **Custom Tools**:
  - Pipeline de preparação de dados automatizado utilizando `dataprep.py`.
- **Language Model**: LLM Gemini.

## Como Funciona
1. Os dados são requisitados pela aplicação usando a API da Câmara dos Deputados.
2. O arquivo `dataprep.py` processa os dados e os organiza de forma estruturada.
3. Utilizando um LLM (Gemini), os dados processados são sumarizados em insights valiosos.
4. O arquivo `dashboard.py` apresenta os dados e insights em um ambiente interativo com três telas principais:

   - **Overview**: Uma visão geral das informações dos deputados, incluindo análises resumidas e insights processados pela IA.
   - **Despesas**: Tela interativa com um selectbox para explorar os gastos detalhados de cada deputado.
   - **Proposições**: Apresenta dados processados de `dataprep.py` em formato de tabela, permitindo análise rápida e objetiva.

## How to Run
1. **Instale as dependências:**
```python
pip install -r requirements.txt
```

2. **Configure o ambiente:**
Certifique-se de que o arquivo `dataprep.py` está configurado para acessar a API da Câmara dos Deputados.

3. **Inicie a aplicação Streamlit:**
```python
streamlit run dashboard.py
```


> [!NOTE]
> É necessário que você esteja dentro da pasta `src` para conseguir rodar as questões do arquivo `dataprep.py`.


> [!IMPORTANT]
> As funções criadas estão comentadas. Sugiro que, observe o código completo e deixe comentado as questões que não for rodar no momento, a partir que for rodando, descomente e rode outra questão.
