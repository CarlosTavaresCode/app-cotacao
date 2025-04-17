import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime
import os
import csv
import pandas as pd
import plotly.express as px


# Configuração da página
st.set_page_config(page_title="Cotações em Tempo Real", page_icon='💰', layout='centered')

st.title(" 💰 Cotações em tempo real")
st.write("Clique no botão para atualizar as cotações")


# Check para auto update
auto_update = st.checkbox(" 🔁 Atualizar automaticamente a cada 10 segundos")

if auto_update:
    st_autorefresh(interval=10 * 1000, key='auto_refresh')

#Criando função para requisição da API

def consultar_cotacoes():
    url = 'https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BRL-USD,BRL-EUR'
    response = requests.get(url)

    if response.status_code == 200:
        dados = response.json()
        return {
        "USDBRL": float(dados['USDBRL']['bid']),
        "EURBRL": float(dados['EURBRL']['bid']),
        "BRLUSD": 1/float(dados['BRLUSD']['bid']),
        "BRLEUR":1/float(dados['BRLEUR']['bid']),
        "hora": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }

    else:
        return None


# Botão para atualizar (manual)

if st.button(" 🔄 Atualizar agora"):
    st.session_state['atualizar'] = True


def exibir_dados():
    cotacoes = consultar_cotacoes()

    if cotacoes:
        st.write(f" Última atualização: {cotacoes['hora']}")
        st.metric("USD -> BRL", f"R${cotacoes['USDBRL']:.2f}")
        st.metric("EUR -> BRL", f"R${cotacoes['EURBRL']:.2f}")
        st.metric("BRL -> USD", f"R${cotacoes['BRLUSD']:.2f}")
        st.metric("BRL -> EUR", f"R${cotacoes['BRLEUR']:.2f}")

        salvar_em_csv(cotacoes)


    else:
        st.error("Erro ao consultar a API!")



def salvar_em_csv(cotacoes, caminho='data/cotacoes.csv'):
    
    # Vamos garantir que a pasta exista
    os.makedirs(os.path.dirname(caminho), exist_ok = True)


    # Checando se o arquivo já estive, assim escrevemos o cabeçalho
    arquivo_existe = os.path.isfile(caminho)


    with open(caminho, mode='a', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)


        # Escrevendo o cabeçalho se o arquivo for novo

        if not arquivo_existe:
            writer.writerow(['Data/Hora', 'USD -> BRL', 'EUR -> BRL', 'BRL -> USD', 'BRL -> EUR'])


        writer.writerow([
            cotacoes['hora'],
            round(cotacoes['USDBRL'],4 ),
            round(cotacoes['EURBRL'],4 ),
            round(cotacoes['BRLUSD'],4 ),
            round(cotacoes['BRLEUR'],4 ),
        ])    


def exibir_grafico(caminho_csv='data/cotacoes.csv'):
    if not os.path.exists(caminho_csv):
        st.info("Ainda não há dados suficientes para exibir o gráfico! ")
        return
    
    df = pd.read_csv(caminho_csv)
    df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])

    # filtrando o período
    opcoes_periodo = {
        "Últimas 24 horas": 1,
        "Últimos 7 dias": 7,
        "Últimos 30 dias": 30,
        "Todo o período":None
    }
    
    periodo_escolhido = st.selectbox(" Selecione o período", list(opcoes_periodo.keys()))

    if opcoes_periodo[periodo_escolhido]:
        dias = opcoes_periodo[periodo_escolhido]
        data_limite = datetime.now() - pd.Timedelta(days=dias)
        df = df[df['Data/Hora'] >= data_limite]



    # Selecionando colunas de interesse para o gráfico
    df_plot = df[['Data/Hora', 'USD -> BRL', 'EUR -> BRL']]

    fig = px.line(df_plot, x = 'Data/Hora', y=['USD -> BRL', 'EUR -> BRL'],
                  labels = {'value': 'Cotação', 'variable': 'Moeda'},
                  title = '📈 Variação das Cotações')
        
    st.plotly_chart(fig, use_container_width=True)

    # Exportar o gráfico

    with st.expander(" Exportar gráfico"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("  Exportar como PNG"):
                fig.write_image("data/grafico_cotacoes.png", format = 'png')
                st.sucess("imagem salva como 'data/grafico_cotacoes.png")

        with col2:
            if st.button(" Exportar como PDF"):
                fig.write_image("data/grafico_cotacoes.pdf", format = 'pdf')
                st.suceess("PDF salvo como 'data/grafico_cotacoes.pdf")        


if __name__ == '__main__':
    exibir_dados()
    st.divider() # Linha para separação
    st.subheader("Histórico de Variação")
    exibir_grafico()

