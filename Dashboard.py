import streamlit as st
#EXECUTAR O CÓDIGO NO TERMINAL USANDO OS COMANDOS: .\venv\Scripts\activate e depois streamlit run Dashboard.py
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

dados = pd.read_csv('estoque.csv')
#não funciona o filtro por região até a url da API voltar a ficar ativa
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2021)

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtro_marcas = st.sidebar.multiselect('Marcas', dados['Marca'].unique())
if filtro_marcas:
    dados = dados[dados['Marca'].isin(filtro_marcas)]

##Tabelas
### Tabelas de receita
receita_estados = dados.groupby('Local da compra')[['Valor']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Valor', ascending = False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Valor'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.strftime('%b')

receita_categorias = dados.groupby('Categoria')[['Valor']].sum().sort_values('Valor', ascending = False)

### Tabelas de quantidade de vendas
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Valor'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Valor', ascending = False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Valor'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.strftime('%b')

vendas_categorias = dados.groupby('Categoria')[['Valor']].count().sort_values('Valor', ascending = False)

### Tabelas marcas
marcas = pd.DataFrame(dados.groupby('Marca')['Valor'].agg(['sum', 'count']))

## Gráficos
### Gráficos de receita
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Valor',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Valor',
                             markers = True,
                             range_y = (0, 1299),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita Mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Valor',
                             text_auto = True,
                             title = 'Top estados (receita)')

fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por categoria')

fig_receita_categorias.update_layout(yaxis_title = 'Receita')

### Gráficos de vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                 lat = 'lat',
                                 lon = 'lon',
                                 scope = 'south america',
                                 size = 'Valor',
                                 template = 'seaborn',
                                 hover_name = 'Local da compra',
                                 hover_data = {'lat': False, 'lon': False},
                                 title = 'Vendas por estado')

fig_vendas_mensal = px.line(vendas_mensal,
                            x = 'Mes',
                            y = 'Valor',
                            markers = True,
                            range_y = (0, 4),
                            color = 'Ano',
                            line_dash = 'Ano',
                            title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                            x = 'Local da compra',
                            y = 'Valor',
                            text_auto = True,
                            title = 'Top 5 estados')

fig_vendas_estados.update_layout(yaxis_title = 'Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias,
                               text_auto = True,
                               title = 'Vendas por categoria')

fig_vendas_categorias.update_layout(showlegend = False, yaxis_title = 'Quantidade de vendas')

## Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Marcas'])
with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Valor'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Valor'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)
with aba3:
    qtd_marcas = st.number_input('Quantidade de marcas', 1, 7, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Valor'].sum(), 'R$'))
        fig_receita_marcas = px.bar(marcas[['sum']].sort_values('sum', ascending = False).head(qtd_marcas),
                                    x = 'sum',
                                    y = marcas[['sum']].sort_values('sum', ascending = False).head(qtd_marcas).index,
                                    text_auto = True,
                                    title = f'Top {qtd_marcas} marcas (receita)')
        st.plotly_chart(fig_receita_marcas)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_marcas = px.bar(marcas[['count']].sort_values('count', ascending = False).head(qtd_marcas),
                                    x = 'count',
                                    y = marcas[['count']].sort_values('count', ascending = False).head(qtd_marcas).index,
                                    text_auto = True,
                                    title = f'Top {qtd_marcas} marcas (quantidade de vendas)')
        st.plotly_chart(fig_vendas_marcas)