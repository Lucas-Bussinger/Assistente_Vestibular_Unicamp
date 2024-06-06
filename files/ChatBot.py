import VestScrapper
import os
import FuncoesChatBot
from langchain_core.messages import HumanMessage, AIMessage
import csv
import FuncoesComunicacao
import time


#pegando os parametros escolhidos para o modelo
dict_data = {}
with open("parametros.csv", 'r', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        dict_data[row["nome"]] = row["valor"]


max_tokens = int(dict_data["max_tokens"])
overlap_arquivo = int(dict_data["overlap_arquivo"])
temperatura = float(dict_data["temperatura"])
nome_modelo_llm = str(dict_data["nome_modelo_llm"])
web_page = str(dict_data['web_page'])
output_file = str(dict_data["output_file"])

#pegando a Resolução GR-031/2023, de 13/07/2023 e transcrevendo para o arquivo de texto "Vestibular_Unicamp_2024.txt"
#isso será feito apenas se o arquivo ainda não estiver baixado, 
#para posteriormente o modelo de LLm ser treinado com base neste arquivo

if output_file not in os.listdir():
    VestScrapper.scrap(web_page, output_file)


api_key = FuncoesComunicacao.ler("files_apoio/openai_api_key.txt")




#1 - criar o modelo llm

llm = FuncoesChatBot.criar_llm(max_tokens, temperatura, env_loaded=False,api_key= api_key, modelo = nome_modelo_llm)

#2 - carregar o arquivo txt e salvar na base de dados vetorizada
#2.1 repartindo o documento em partes menores para ser vetorizado

documento_repartido = FuncoesChatBot.documento_repartido(output_file, max_tokens, overlap_arquivo)

#2.2: vetorizando o documento

doc_vetorizado = FuncoesChatBot.vetorizar_documento(documento_repartido, env_loaded=False, api_key=api_key)

#3: montando a chain_recuperadora
#3.1: criando o prompt ( ja pré definido em FuncoesChatBot.py)

prompt = FuncoesChatBot.criar_promp()

#3.2: criando a chain_recuperadora

chain_recuperadora = FuncoesChatBot.criar_chain_recuperadora(llm, prompt, doc_vetorizado)

#criando o histórico de conversa e rodando o chat
historico_chat = []


last_write_stuff = ''
inicialized_stuff = FuncoesComunicacao.ler("files_apoio/last_chat_operation.txt")
iteration = 0

FuncoesComunicacao.escrever("files_apoio/bot_running.txt", "1")




while True:
    # para trabalhar a comunicação com o site:
    current_read_stuff = FuncoesComunicacao.ler("files_apoio/last_chat_operation.txt")

    if current_read_stuff.lower() == 'sair' and iteration != 0:
        FuncoesComunicacao.escrever("files_apoio/bot_running.txt", "0")
        break

    if current_read_stuff != last_write_stuff and current_read_stuff != inicialized_stuff:
        #verificar se essa foi a primeira chamada
        if iteration == 0:
            iteration = 1
        
        pergunta = current_read_stuff
        
        if pergunta.lower() == 'sair':
            FuncoesComunicacao.escrever("files_apoio/bot_running.txt", "0")
            break

        resposta_ai = FuncoesChatBot.processar_chat(chain_recuperadora, pergunta, historico_chat)
        last_write_stuff = resposta_ai

        historico_chat.append(HumanMessage(content = pergunta))
        historico_chat.append(AIMessage(content = resposta_ai))


        FuncoesComunicacao.escrever("files_apoio/last_chat_operation.txt", last_write_stuff)

        # A AI lembrará apenas das 5 últimas entradas e saídas, pois se não ela ficaria muito lenta.
        if len(historico_chat) > 10:
            for _ in range(2):
                historico_chat.pop(0)
    
    else:
        time.sleep(0.2)
    