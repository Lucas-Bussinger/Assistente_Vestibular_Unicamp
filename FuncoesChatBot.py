from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import MessagesPlaceholder



def criar_llm(max_tokens, temperature, modelo = "gpt-4-turbo", env_loaded = False, api_key = ''):
    #criando o modelo de large languague model
    if not env_loaded and len(api_key) > 0:
        llm = ChatOpenAI(model=modelo,
                        api_key=api_key,
                        temperature=temperature,
                        max_tokens=max_tokens)
    
    else:
        llm = ChatOpenAI(model=modelo,
                        temperature=temperature,
                        max_tokens=max_tokens)
    
    return llm

def documento_repartido(path_to_txt_document, chunk_size, chunk_overlap):
    #repartindo o documento em partes menores para mais para frente estas partes serem tokenizadas
    loader = TextLoader(path_to_txt_document, encoding= 'utf-8')
    texto_integro = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size= chunk_size,
        chunk_overlap = chunk_overlap
    )

    splitted = splitter.split_documents(texto_integro)

    return splitted

def vetorizar_documento(documento_repartido, api_key = '', env_loaded = False):
    # transforma sentenças em representações núméricas ( matemáticas )

    if not env_loaded and len(api_key) > 0:
        embeddings = OpenAIEmbeddings(model = 'text-embedding-3-large', api_key=api_key)
    else:
        embeddings = OpenAIEmbeddings(model = 'text-embedding-3-large')

    #cria uma base de dados vetprizada( de rápido acesso ) dos embeddings
    # escolha do FAISS: otimizará a busca por similaridade mais para frente ( similarity search )
    doc_vetorizado = FAISS.from_documents(documento_repartido, embedding= embeddings)

    return doc_vetorizado

def criar_promp():
    # aqui será criado o contexto para que o modelo consiga responder às perguntas do usuário e relembrar das perguntas anteriores

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Responda a pergunta do usuario de acordo com o contexto, caso a informação
         nao esteja no contexto e nem de para inferir, diga que nao sabe a resposta daquela pergunta
         Contexto: {context}
         Pergunta: {input}"""),
        MessagesPlaceholder(variable_name= "historico_chat"),
        ("human", "{input}")
         
    ])

    return prompt

def criar_chain_recuperadora(llm, prompt, doc_vetorizado):
    #chain é uma cadeia de operações que refinará os dados de entrada para que 
    #o modelo de large language model consiga operar mais eficientemente

    # criando uma cadeia capaz de recuperar dados do documento, e mais para frente, do histórico do chat
    chain = create_stuff_documents_chain(llm = llm,
                                         prompt = prompt)
    
    recuperador = doc_vetorizado.as_retriever(search_kwargs = {"k": 5}) # retorna os 5 pedaços mais relevantes do documento

    # com o uso da create_retrieval_chain ele já esta setado para  fazer um similarity_search no arquivo a partir da entrada do usuário
    #isso pegará as 5 partes mais relevantes do arquivo de acordo com a pergunta do usuário, sendo enviado como contexto para a llm
    chain_recuperadora = create_retrieval_chain(
        recuperador, 
        chain
    )

    return chain_recuperadora

def processar_chat(chain_recuperadora, pergunta_usuario, historico_chat):
    #processando um request de pergunta
    resposta_ai = chain_recuperadora.invoke({
        "input": pergunta_usuario,
        "historico_chat": historico_chat
    })

    return resposta_ai['answer']
