import streamlit as st
import requests
import random
from collections import Counter
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do Airtable
API_KEY = os.getenv("API_KEY")
BASE_ID = 'appbilLuJlIRT6n0B'
TABLE_NAME = 'inscritos'

# URL do endpoint do Airtable
url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'

# Headers para a requisição
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Opções de cores disponíveis
cores = ['Laranja', 'Vermelho', 'Verde', 'Roxo']

# Função para buscar os registros do Airtable
def get_nomes_sem_cor():
    params = {
        'filterByFormula': 'OR({Cor} = "", {Cor} = BLANK())',
        'fields[]': ['Nome', 'Cor']  # Adicionamos a coluna 'Cor' para rastrear as cores atribuídas
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        records = response.json().get('records', [])
        nomes = [record['fields']['Nome'] for record in records]
        return records, nomes  # Retorna os registros e os nomes
    else:
        st.error("Erro ao buscar dados do Airtable")
        return [], []

# Função para buscar todas as cores já atribuídas
def get_cores_atribuidas():
    params = {
        'fields[]': ['Cor']  # Pega apenas a coluna de cores
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        records = response.json().get('records', [])
        cores_atribuidas = [record['fields'].get('Cor') for record in records if 'Cor' in record['fields']]
        return cores_atribuidas
    else:
        st.error("Erro ao buscar as cores atribuídas")
        return []

# Função para distribuir cores proporcionalmente
def escolher_cor_proporcional():
    # Verifica as cores que já foram atribuídas para manter a proporcionalidade
    cores_atribuidas = get_cores_atribuidas()
    
    # Contador de quantas vezes cada cor já foi atribuída, inicializando com zero para cada cor
    contagem_cores = Counter(cores_atribuidas)
    for cor in cores:
        if cor not in contagem_cores:
            contagem_cores[cor] = 0
    
    # Lista com as cores que foram menos usadas
    menos_usadas = [cor for cor in cores if contagem_cores[cor] == min(contagem_cores.values())]
    
    # Retorna uma cor aleatória entre as menos usadas
    return random.choice(menos_usadas)

# Função para atualizar a cor no Airtable
def atualizar_cor(record_id, nova_cor):
    data = {
        'fields': {
            'Cor': nova_cor
        }
    }
    
    response = requests.patch(f'{url}/{record_id}', headers=headers, json=data)
    
    if response.status_code == 200:
        st.success(f'A cor {nova_cor} foi selecionada com sucesso!')
    else:
        st.error("Erro ao atualizar a cor no Airtable")

# Função para redirecionar o usuário dependendo da cor
def redirecionar_por_cor(cor):
    urls = {
        'Laranja': 'https://drive.google.com/file/d/182jmtsY5r3UMbHuYN6WdQf1-RJfkRmzi/preview',
        'Vermelho': 'https://drive.google.com/file/d/1IP4gNs4_CRzQ02eifXbCHUCDAtEhPnMv/preview',
        'Verde': 'https://drive.google.com/file/d/1YT7TCpjm7aKSRrRHups8z23decQOVrxz/preview',
        'Roxo': 'https://drive.google.com/file/d/14QtF04Bt34u2yWjO_xFuLvso7N14A2TA/preview'
    }
    
    if cor in urls:
        st.markdown(f"<meta http-equiv='refresh' content='0; url={urls[cor]}'>", unsafe_allow_html=True)


# Busca os nomes onde a coluna "Cor" está vazia
records, nomes = get_nomes_sem_cor()

# Exibe o formulário
st.title('Descubra a COR da sua TRIBO')

with st.form(key='formulario_cor'):
    nome_selecionado = st.selectbox('Selecione o Seu Nome', nomes, index=None)
    
    # Pergunta 1
    pergunta_1 = st.radio(
        "Quando você enfrenta um desafio, como você costuma reagir?",
        ('a) Eu busco força e não desisto facilmente.',
         'b) Tento encontrar soluções criativas e relevantes para o problema.',
         'c) Fico fiel ao meu estilo e valores, sem me deixar influenciar.',
         'd) Procuro envolver outras pessoas para superarmos juntos.'),
        index=None
    )
    
    # Pergunta 2
    pergunta_2 = st.radio(
        "O que é mais importante para você em um grupo?",
        ('a) Que todos estejam comprometidos e focados no objetivo.',
         'b) Que sejamos impactantes e façamos a diferença.',
         'c) Que cada um seja autêntico e verdadeiro consigo mesmo.',
         'd) Que todos trabalhem em unidade e sintonia.'),
        index=None
    )
    
    # Pergunta 3
    pergunta_3 = st.radio(
        "Como você gosta de passar seu tempo livre?",
        ('a) Participando de atividades desafiadoras e estimulantes.',
         'b) Fazendo algo que tenha impacto e seja importante para os outros.',
         'c) Aproveitando para me expressar de forma verdadeira e autêntica.',
         'd) Estando com amigos e aproveitando momentos em grupo.'),
        index=None
    )
    
    enviar = st.form_submit_button('Enviar')

# Ao submeter o formulário
if enviar and nome_selecionado:
    # Seleciona uma cor proporcionalmente
    cor_selecionada = escolher_cor_proporcional()
    
    # Encontra o ID do registro correspondente ao nome selecionado
    record_id = next(record['id'] for record in records if record['fields']['Nome'] == nome_selecionado)
    
    # Atualiza o registro no Airtable
    atualizar_cor(record_id, cor_selecionada)
    
    # Exibe a cor selecionada
    st.write(f"A cor atribuída para {nome_selecionado} foi: {cor_selecionada}")
    
    # Exibe visualmente a cor associada
    st.markdown(f"<div style='background-color:{cor_selecionada.lower()};padding:10px;color:white;'>Cor: {cor_selecionada}</div>", unsafe_allow_html=True)
    
    # Redireciona o usuário para a URL baseada na cor atribuída
    redirecionar_por_cor(cor_selecionada)
