from datetime import datetime, timedelta
import json
import os
import pytz
from dateutil import parser
import requests

API_KEY = os.environ.get('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")

def chamar_openai_api(texto):
    """Chama a API do OpenAI diretamente"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {
                'role': 'system',
                'content': """
                    Você é um assistente de agenda que extrai informações de comandos em português.
                    Retorne apenas um JSON com:
                    {
                        "acao": "criar" ou "consultar",
                        "data": data em ISO format,
                        "titulo": título do evento (para criar),
                        "email": email da pessoa (para consultar),
                        "duracao": duração em minutos (padrão 60)
                    }
                """
            },
            {
                'role': 'user',
                'content': texto
            }
        ]
    }
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        raise Exception(f"Erro na API do OpenAI: {response.text}")
    
    return response.json()

def processar_comando(texto, service):
    """Processa o comando do usuário usando GPT"""
    try:
        resposta = chamar_openai_api(texto)
        conteudo = resposta['choices'][0]['message']['content']
        dados = json.loads(conteudo)
        
        if dados["acao"] == "criar":
            return criar_evento(service, dados)
        elif dados["acao"] == "consultar":
            return consultar_agenda(service, dados)
        
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao processar comando: {str(e)}"
        }

def criar_evento(service, dados):
    """Cria um evento baseado nos dados processados"""
    try:
        inicio = parser.parse(dados["data"])
        fim = inicio + timedelta(minutes=dados.get("duracao", 60))
        
        evento = {
            'summary': dados["titulo"],
            'start': {
                'dateTime': inicio.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': fim.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            }
        }
        
        evento_criado = service.events().insert(
            calendarId='primary',
            body=evento
        ).execute()
        
        return {
            "status": "sucesso",
            "mensagem": f"Evento '{dados['titulo']}' criado para {inicio.strftime('%d/%m/%Y %H:%M')}",
            "link": evento_criado['htmlLink']
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao criar evento: {str(e)}"
        }

def consultar_agenda(service, dados):
    """Consulta a agenda de uma pessoa"""
    try:
        data = parser.parse(dados["data"])
        inicio = data.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
        fim = data.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=dados.get("email", 'primary'),
            timeMin=inicio,
            timeMax=fim,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return {
                "status": "sucesso",
                "mensagem": f"Nenhum evento encontrado para {data.strftime('%d/%m/%Y')}"
            }
        
        eventos_formatados = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_time = parser.parse(start).strftime('%H:%M')
            eventos_formatados.append(f"- {start_time}: {event['summary']}")
        
        return {
            "status": "sucesso",
            "mensagem": f"Eventos encontrados para {data.strftime('%d/%m/%Y')}:\n" + "\n".join(eventos_formatados)
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao consultar agenda: {str(e)}"
        } 