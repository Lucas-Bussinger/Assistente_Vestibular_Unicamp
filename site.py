import streamlit as st
import FuncoesComunicacao
import time
import subprocess
import requests
import VestScrapper
import FuncoesChatBot
import csv
import portalocker
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import MessagesPlaceholder
import json
from bs4 import BeautifulSoup as bs




# type: ignore

#toda vez que o usuário passa um comando, o arquivo inteiro é recarregado pelo streamlit
# por isso o ChatBot precisa rodar em separados, se comunicando com o site a partir do arquivo "last_chat_operation.txt"
st.title("Assistente para Vestibular Unicamp 2024")

#inicializar hitorico de chat

if "messages" not in st.session_state:
    st.session_state.messages = []

#mostrando mensagens do chat
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message["content"])


#reagir a input do usuário
prompt = st.chat_input("Mensagem: ('ativar: sua_api_key_da_openai' para ativar bot), ( 'sair' para sair ) ")

if prompt:
    
    #mostrar mensagem do usuário na tela
    with st.chat_message("user"):
        st.markdown(prompt)
    
    last_site_read = prompt
    FuncoesComunicacao.escrever("files_apoio/last_chat_operation.txt", last_site_read)

    #verificar se o bot está rodando
    bot_running = FuncoesComunicacao.ler("files_apoio/bot_running.txt")

    #verificar se o usuário requisitou a ativação do bot
    if last_site_read[0:6] == 'ativar' and bot_running == '0':
        
        api_key = last_site_read.split(":")[1].strip()
        FuncoesComunicacao.escrever("files_apoio/openai_api_key.txt", api_key)

        subprocess.Popen(["python","ChatBot.py"])
        time.sleep(18)
        

    # adicionar mensagem do usuário para o histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    new_read = last_site_read

    # se o bot estiver ativo e o prompt nao for um comando: rodar a resposta do bot
    if prompt != 'sair' and prompt != "ativar" and bot_running == "1":
        while new_read == last_site_read:
            new_read = FuncoesComunicacao.ler("files_apoio/last_chat_operation.txt")
            time.sleep(0.1)

    response = new_read

    if prompt[0:6] == 'ativar':
        response = 'Bot Ativado'
    if prompt == 'sair':
        FuncoesComunicacao.escrever("files_apoio/openai_api_key.txt", ' ')
        response = "Bot Desativado"

    #mostrar mensagem do bot:
    with st.chat_message("assistant"):
        st.markdown(response) # mudar isso aqui
    
    #adicionar esposta do bot ao histórico
    st.session_state.messages.append({"role": "assistant", "content": response})

