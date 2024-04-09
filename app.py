# Arquivo principal do Streamlit

#from api_functions import create_headers, create_thread_run, list_messages, create_message_and_run
#from utils import iniciar_conversa, manter_conversa
import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os
import time
import random

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Agora, você pode acessar a variável de ambiente como antes
#api_token = os.getenv('OPENAI_API_KEY', 'Token Não Encontrado')
assistant_id = os.getenv('ASSISTANT_ID', 'Assistant ID Não Encontrado')


#Teste token
#st.write(f"Token: {api_token}")
#st.write(f"Assistant_id: {assistant_id}")



# Função para criar os headers com o token fornecido pelo usuário
def create_headers():
    # Verifica se o token foi armazenado no estado da sessão
    if 'api_token' in st.session_state and st.session_state['api_token']:
        return {
            'Authorization': f"Bearer {st.session_state['api_token']}",
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v1'
        }
    else:
        st.error('Token de API não configurado. Por favor, insira seu token na barra lateral.')
        return None  # Retorna None para indicar que os headers não puderam ser criados


# Inicializa thread_id no st.session_state se ainda não estiver definido
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None

# Passo 3: Função para Criar um Thread Run - Modificada para atualizar st.session_state
def create_thread_run(initial_question):
    ###
        # Verifica se os headers estão disponíveis no estado da sessão
    if 'headers' in st.session_state and st.session_state['headers'] is not None:
        headers = st.session_state['headers']
    else:
        st.error('Headers não configurados. Por favor, insira o token de API na barra lateral.')
        return None, 'Headers não configurados.'
    ###

    url = "https://api.openai.com/v1/threads/runs"
    data = json.dumps({
        "assistant_id": assistant_id,
        "thread": {
            "messages": [
                {"role": "user", "content": initial_question}
            ]
        }
    })
    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()

    if 'thread_id' in response_json:
        st.session_state.thread_id = response_json['thread_id']
        return st.session_state.thread_id, "Thread criado com sucesso."
    else:
        return None, f"Erro: 'thread_id' não encontrado na resposta. Resposta recebida: {response_json}"

#Passo 4: Função para Listar Mensagens
# Modificação no uso de list_messages para acessar thread_id do st.session_state
def list_messages():
    ###
        # Verifica se os headers estão disponíveis no estado da sessão
    if 'headers' in st.session_state and st.session_state['headers'] is not None:
        headers = st.session_state['headers']
    else:
        st.error('Headers não configurados. Por favor, insira o token de API na barra lateral.')
        return None, 'Headers não configurados.'
    ###

    if st.session_state.thread_id is None:
        return "", "Erro: thread_id não definido."

    url = f"https://api.openai.com/v1/threads/{st.session_state.thread_id}/messages"
    response = requests.get(url, headers=headers)
    response_json = response.json()

    ultima_mensagem = ""  # Inicializa a variável que armazenará a última mensagem do assistente

    if response_json.get('data') and len(response_json['data']) > 0:
        # Percorre as mensagens como recebidas, começando pela mais recente
        for message in response_json['data']:
            if message['role'] == 'assistant' and message['content']:
                ultima_mensagem = message['content'][0].get('text', {}).get('value', '')
                break  # Encontra a primeira (mais recente) resposta do assistente e sai do loop
        if not ultima_mensagem:  # Caso nenhuma mensagem do assistente tenha sido encontrada
            return "", "Nenhuma resposta do assistente encontrada."
    else:
        return "", "Nenhuma mensagem encontrada."

    return ultima_mensagem, ""  # Retorna a última mensagem do assistente e uma string vazia para erro


#Passo 5: Função para Criar Mensagem #Passo 6: Função para Criar um Run
def create_message_and_run(user_message):
    ###
        # Verifica se os headers estão disponíveis no estado da sessão
    if 'headers' in st.session_state and st.session_state['headers'] is not None:
        headers = st.session_state['headers']
    else:
        st.error('Headers não configurados. Por favor, insira o token de API na barra lateral.')
        return None, 'Headers não configurados.'
    ###

    if st.session_state.thread_id is None:
        return "Erro: thread_id não definido.", False

    # Primeiro, cria a mensagem
    message_url = f"https://api.openai.com/v1/threads/{st.session_state.thread_id}/messages"
    message_data = {
        "role": "user",
        "content": user_message
    }
    message_response = requests.post(message_url, headers=headers, json=message_data)
    message_response_json = message_response.json()

    # Verifica se a mensagem foi criada com sucesso antes de prosseguir
    if 'id' not in message_response_json:
        return f"Falha ao criar a mensagem. Resposta recebida: {message_response_json}", False

    # Em seguida, cria o run
    run_url = f"https://api.openai.com/v1/threads/{st.session_state.thread_id}/runs"
    run_data = {"assistant_id": assistant_id}
    run_response = requests.post(run_url, headers=headers, json=run_data)
    run_response_json = run_response.json()

    if 'id' in run_response_json:
        # Pode ser necessário adaptar esta parte para extrair e retornar informações úteis do run
        return "Mensagem enviada e run criado com sucesso.", True
    else:
        return f"Falha ao criar o run. Resposta recebida: {run_response_json}", False

##################
# Mensagens de espera
mensagens_espera = [
    "Ainda estou vasculhando os meandros do conhecimento. Só mais um pouquinho...",
    "Conferindo com os gurus aqui no PNCP. Já te trago uma resposta!",
    "Estou quase lá! Organizando as palavras para te surpreender.",
    "Um momento, por favor. Estou consultando os sábios da internet.",
    "Dando os últimos retoques na sua resposta... Quase como um artista!",
    "Me dê um segundinho... Ainda estou aprendendo a ser rápido como um raio!",
    "Consultando os oráculos... Eles geralmente sabem tudo!",
    "Aguenta firme! Estou buscando algo realmente interessante para você.",
    "Só mais um momento. Estou preparando uma resposta digna de um prêmio!",
    "Transformando café em código... e em breve, em sua resposta!"
]
###################
# Inicializa `thread_id` no st.session_state se ainda não estiver definido
#if 'thread_id' not in st.session_state:
#    st.session_state.thread_id = None

# Inicializa a variável para controlar a última resposta conhecida
if 'mensagem_desatualizada' not in st.session_state:
    st.session_state.mensagem_desatualizada = ""


def iniciar_conversa(pergunta_usuario):
    # Se é a primeira mensagem da conversa, cria um novo thread
    if 'thread_id' not in st.session_state or st.session_state.thread_id is None:
        _, msg = create_thread_run(pergunta_usuario)  # Certifique-se de ajustar conforme a assinatura da sua função
        st.write("Um momento, por favor. Estou consultando os sábios do PNCP.")
        time.sleep(5)

    tentativas = 0
    mensagem_desatualizada, erro = "", ""
    while tentativas < 10:
        mensagem_desatualizada, erro = list_messages()  # Ajuste conforme a assinatura da sua função
        if mensagem_desatualizada and mensagem_desatualizada != st.session_state.get('mensagem_desatualizada', ''):
            st.session_state.mensagem_desatualizada = mensagem_desatualizada
            st.write("Resposta do Chatbot:", mensagem_desatualizada)
            break
        elif erro:
            st.error(erro)  # Exibe erro se não conseguir obter a resposta
            break
        else:
            wait_message = st.empty()
            wait_message.write(random.choice(mensagens_espera))
            time.sleep(5)  # Ajuste o tempo conforme necessário
            wait_message.empty()
            tentativas += 1
            if tentativas == 10:  # Se atingir o número máximo de tentativas sem resposta
                st.error("Não foi possível obter uma resposta após várias tentativas.")

def manter_conversa(pergunta_usuario):
    # Para mensagens subsequentes, envia a mensagem e processa a resposta
    msg_enviada, sucesso = create_message_and_run(pergunta_usuario)
    if not sucesso:
        st.error(msg_enviada)  # Exibe erro se não conseguir enviar a mensagem
        return

    # Tenta obter a resposta mais recente do chatbot
    resposta_atual, erro = "", ""
    for _ in range(10):  # Tenta até 10 vezes esperar por uma nova resposta
        resposta_atual, erro = list_messages()
        if erro:
            st.error(erro)  # Exibe erro se não conseguir obter a resposta
            return

        if st.session_state.mensagem_desatualizada != resposta_atual:
            st.session_state.mensagem_desatualizada = resposta_atual
            st.write("Resposta do Chatbot:", resposta_atual)  # Exibe a resposta atual do chatbot
            break
        else:
            # Atualiza a mensagem de espera
            wait_message = st.empty()  # Recria o placeholder para evitar sobreposição de mensagens de espera
            wait_message.write(random.choice(mensagens_espera))
            time.sleep(5)
            wait_message.empty()

# Construção da interface de usuário com Streamlit
st.title('ChatPNCP')

###################
# Título da sidebar
st.sidebar.title('Configuração de acesso')

# Input para o usuário inserir sua chave
user_token = st.sidebar.text_input('Digite sua chave', '')

# Ação ao clicar no botão
# Ação ao clicar no botão
if st.sidebar.button('Clique aqui'):
    if user_token:  # Verifica se o usuário inseriu algo
        # Atualiza o token no estado da sessão para uso posterior
        st.session_state['api_token'] = user_token
        st.session_state['headers'] = create_headers()  # Atualiza os headers no estado da sessão
        #st.write(st.session_state['headers'])  # Corrigido para exibir corretamente os headers
        st.sidebar.success('Chave enviada, pode iniciar seus testes!')
    else:
        st.sidebar.error('Por favor, insira uma chave válida.')
###################

st.session_state.pergunta = st.text_input('O que você gostaria de saber do PNCP:', key='nova_pergunta')
if st.button('Enviar', key='enviar_pergunta'):
    pergunta_usuario = st.session_state.pergunta  # Obtém a pergunta do usuário do estado da sessão
    if 'mensagem_desatualizada' not in st.session_state or st.session_state.mensagem_desatualizada == "":
        iniciar_conversa(pergunta_usuario)
    else:
        manter_conversa(pergunta_usuario)
