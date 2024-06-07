import FuncoesComunicacao
import time
import json
import subprocess

#pegando a openai_api_key fornecida pelo usuário:
api_key = input("Digite a API_KEY da openai: ").strip()
FuncoesComunicacao.escrever('files_apoio/openai_api_key.txt', api_key)

#iniciando o ChatBot em paralelismo com este programa
subprocess.Popen(['python','ChatBot.py'])
time.sleep(12)


def pegar_resposta_ai(pergunta: str):
    #retornando a resposta do ChatBot para a pergunta
    FuncoesComunicacao.escrever("files_apoio/last_chat_operation.txt", pergunta)
    last_read = pergunta
    while last_read == pergunta:
        last_read = FuncoesComunicacao.ler('files_apoio/last_chat_operation.txt')

        time.sleep(0.16)
    
    return last_read


with open('files_apoio/perguntas_respostas.json', 'r', encoding='utf-8') as file:
    # Carreguando os dados do arquivo
    dados = json.load(file)


counter = 0
for dado in dados:
    counter += 1
    pergunta = dado['pergunta']

    resposta_ai = pegar_resposta_ai(pergunta)

    with open("files_apoio/respostas_avaliacao.txt", 'a', encoding='utf-8') as file:
        file.write(f" Pergunta Número {counter}:\n\nPergunta: {pergunta}\n\nResposta esperada: {dado['resposta']}\n\nResposta Obtida: {resposta_ai}\n")

        file.write("\n\n" + "-/"*200 + "\n\n")
        

#Desligando o Bot e retirando a chave openai_api_key do usuário da memória do sistema
FuncoesComunicacao.escrever("files_apoio/last_chat_operation.txt", 'sair')
FuncoesComunicacao.escrever('files_apoio/openai_api_key.txt', ' ')