from flask import Flask, request, jsonify, render_template
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
import os

# Configurações de ambiente
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# Escopos necessários para acessar a Google Agenda
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Serviço de autenticação global
service = None

def salvar_credenciais(creds):
    """Salva as credenciais em um arquivo"""
    try:
        creds_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        with open('token.json', 'w') as token:
            json.dump(creds_data, token)
        return True
    except Exception as e:
        print(f"Erro ao salvar credenciais: {e}")
        return False

def carregar_credenciais():
    """Carrega credenciais salvas"""
    try:
        with open('token.json', 'r') as token:
            creds_data = json.load(token)
            return Credentials.from_authorized_user_info(creds_data, SCOPES)
    except Exception as e:
        print(f"Erro ao carregar credenciais: {e}")
        return None

# Função para autenticar na Google API
def autenticar():
    try:
        # Tenta carregar credenciais existentes
        creds = carregar_credenciais()
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    SCOPES,
                    redirect_uri=os.environ.get('REDIRECT_URI', 'http://localhost:8080/oauth2callback')
                )
                creds = flow.run_local_server(port=0)
                if not salvar_credenciais(creds):
                    raise Exception("Falha ao salvar credenciais")
        
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"Erro ao autenticar: {e}")
        raise e

def get_service():
    """Retorna o serviço, inicializando se necessário"""
    global service
    if service is None:
        service = autenticar()
    return service

# Rota inicial
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint para listar eventos
@app.route('/listar', methods=['GET'])
def listar_eventos():
    try:
        current_service = get_service()
        events_result = current_service.events().list(
            calendarId='primary', maxResults=10, singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        if not events:
            return jsonify({"message": "Nenhum evento encontrado."})
        return jsonify({"events": [
            {"start": event['start'].get('dateTime', event['start'].get('date')), "summary": event['summary']}
            for event in events
        ]})
    except Exception as e:
        print(f"Erro no endpoint /listar: {e}")
        return jsonify({"error": f"Erro ao listar eventos: {str(e)}"}), 500

# Endpoint para criar um evento
@app.route('/criar', methods=['POST'])
def criar_evento():
    try:
        data = request.json

        # Validar dados recebidos
        campos_obrigatorios = ["summary", "location", "start", "end", "attendees"]
        campos_faltantes = [campo for campo in campos_obrigatorios if campo not in data]
        
        if campos_faltantes:
            return jsonify({
                "error": "Dados incompletos na requisição",
                "campos_faltantes": campos_faltantes,
                "status": "erro"
            }), 400

        current_service = get_service()
        evento = {
            'summary': data['summary'],
            'location': data['location'],
            'start': {
                'dateTime': data['start'],
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': data['end'],
                'timeZone': 'America/Sao_Paulo',
            },
            'attendees': [{'email': email} for email in data['attendees']],
        }

        evento_criado = current_service.events().insert(calendarId='primary', body=evento).execute()
        
        return jsonify({
            "message": "Evento criado com sucesso!",
            "link": evento_criado['htmlLink'],
            "detalhes": {
                "id": evento_criado['id'],
                "titulo": evento_criado['summary'],
                "inicio": evento_criado['start']['dateTime'],
                "fim": evento_criado['end']['dateTime'],
                "participantes": [att['email'] for att in evento_criado.get('attendees', [])]
            },
            "status": "sucesso"
        })
    
    except Exception as e:
        erro_msg = str(e)
        print(f"Erro no endpoint /criar: {erro_msg}")
        return jsonify({
            "error": f"Erro ao criar evento: {erro_msg}",
            "status": "erro",
            "detalhes_erro": {
                "tipo": type(e).__name__,
                "mensagem": erro_msg
            }
        }), 500

# Rota para iniciar autenticação
@app.route('/auth')
def auth():
    try:
        get_service()
        return jsonify({
            "message": "Autenticação realizada com sucesso!",
            "status": "sucesso"
        })
    except Exception as e:
        return jsonify({
            "error": f"Erro na autenticação: {str(e)}",
            "status": "erro"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
