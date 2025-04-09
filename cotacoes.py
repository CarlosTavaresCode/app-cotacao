import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime


# Configuração da página
st.set_page_config(page_title="Cotações em Tempo Real", page_icon='💰', layout='centered')

st.title("Cotações em tempo real")
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

    else:
        st.error("Erro ao consultar a API!")

if __name__ == '__main__':
    exibir_dados()

