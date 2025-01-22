from flask import Flask, request, jsonify, render_template, redirect, url_for
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
import os
import pathlib
from datetime import datetime, timedelta
import pytz

# Configurações de ambiente
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configuração de diretórios
DATA_DIR = pathlib.Path("/opt/render/project/src/data")
TOKEN_PATH = DATA_DIR / "token.json"
CREDENTIALS_PATH = DATA_DIR / "credentials.json"

# Cria o diretório de dados se não existir
DATA_DIR.mkdir(exist_ok=True, parents=True)

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
        with open(TOKEN_PATH, 'w') as token:
            json.dump(creds_data, token)
        print(f"Credenciais salvas em: {TOKEN_PATH}")
        return True
    except Exception as e:
        print(f"Erro ao salvar credenciais: {e}")
        return False

def carregar_credenciais():
    """Carrega credenciais salvas"""
    try:
        if not TOKEN_PATH.exists():
            print("Arquivo de token não encontrado")
            return None
            
        with open(TOKEN_PATH, 'r') as token:
            creds_data = json.load(token)
            creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
            
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    print("Renovando token expirado...")
                    creds.refresh(Request())
                    salvar_credenciais(creds)
                else:
                    print("Credenciais inválidas e não podem ser renovadas")
                    return None
            return creds
    except Exception as e:
        print(f"Erro ao carregar credenciais: {e}")
        return None

def get_service():
    """Retorna o serviço, inicializando se necessário"""
    global service
    try:
        if service is None:
            creds = carregar_credenciais()
            if creds and creds.valid:
                service = build('calendar', 'v3', credentials=creds)
            else:
                print("Credenciais não disponíveis ou inválidas")
                return None
        return service
    except Exception as e:
        print(f"Erro ao obter serviço: {e}")
        return None

def reset_service():
    """Reseta o serviço global"""
    global service
    service = None

# Rota inicial
@app.route('/')
def home():
    if get_service() is None:
        reset_service()  # Limpa o serviço se estiver inválido
        return render_template('auth_required.html')
    return render_template('index.html')

# Rota para iniciar autenticação
@app.route('/auth')
def auth():
    try:
        reset_service()  # Limpa qualquer serviço existente
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH,
            SCOPES,
            redirect_uri=os.environ.get('REDIRECT_URI')
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return redirect(authorization_url)
    except Exception as e:
        print(f"Erro na autenticação: {e}")
        return jsonify({
            "error": f"Erro na autenticação: {str(e)}",
            "status": "erro"
        }), 500

# Callback do OAuth2
@app.route('/oauth2callback')
def oauth2callback():
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH,
            SCOPES,
            redirect_uri=os.environ.get('REDIRECT_URI')
        )
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        
        if salvar_credenciais(creds):
            global service
            service = build('calendar', 'v3', credentials=creds)
            return redirect(url_for('home'))
        else:
            return "Erro ao salvar credenciais", 500
    except Exception as e:
        print(f"Erro no callback: {str(e)}")
        return f"Erro no callback: {str(e)}", 500

# Endpoint para listar eventos
@app.route('/listar', methods=['GET'])
def listar_eventos():
    current_service = get_service()
    if current_service is None:
        reset_service()
        return jsonify({"error": "Autenticação necessária", "status": "erro"}), 401
    
    try:
        # Pega parâmetros da requisição
        email = request.args.get('email', 'primary')  # 'primary' é a agenda principal
        data_inicio = request.args.get('inicio')
        data_fim = request.args.get('fim')
        
        # Se não especificou datas, usa próximos 7 dias
        if not data_inicio:
            tz = pytz.timezone('America/Sao_Paulo')
            agora = datetime.now(tz)
            data_inicio = agora.isoformat()
            data_fim = (agora + timedelta(days=7)).isoformat()
        
        events_result = current_service.events().list(
            calendarId=email,
            timeMin=data_inicio,
            timeMax=data_fim,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return jsonify({
                "message": "Nenhum evento encontrado para o período.",
                "periodo": {
                    "inicio": data_inicio,
                    "fim": data_fim
                }
            })
            
        return jsonify({
            "events": [{
                "id": event['id'],
                "summary": event['summary'],
                "start": event['start'].get('dateTime', event['start'].get('date')),
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "location": event.get('location', ''),
                "attendees": [
                    att['email'] for att in event.get('attendees', [])
                ],
                "link": event['htmlLink']
            } for event in events],
            "periodo": {
                "inicio": data_inicio,
                "fim": data_fim
            }
        })
        
    except Exception as e:
        print(f"Erro no endpoint /listar: {e}")
        reset_service()
        return jsonify({"error": f"Erro ao listar eventos: {str(e)}"}), 500

# Endpoint para listar calendários disponíveis
@app.route('/calendarios', methods=['GET'])
def listar_calendarios():
    current_service = get_service()
    if current_service is None:
        reset_service()
        return jsonify({"error": "Autenticação necessária", "status": "erro"}), 401
    
    try:
        calendar_list = current_service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        return jsonify({
            "calendarios": [{
                "id": cal['id'],
                "summary": cal['summary'],
                "primary": cal.get('primary', False),
                "accessRole": cal['accessRole']
            } for cal in calendars]
        })
        
    except Exception as e:
        print(f"Erro ao listar calendários: {e}")
        reset_service()
        return jsonify({"error": f"Erro ao listar calendários: {str(e)}"}), 500

# Endpoint para criar um evento
@app.route('/criar', methods=['POST'])
def criar_evento():
    current_service = get_service()
    if current_service is None:
        reset_service()
        return jsonify({"error": "Autenticação necessária", "status": "erro"}), 401
    
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

        # Ajusta o fuso horário para Brasília
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
            # Adiciona configurações de fuso horário
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
            # Força o fuso horário do evento
            'timeZone': 'America/Sao_Paulo'
        }

        evento_criado = current_service.events().insert(
            calendarId='primary',
            body=evento,
            # Adiciona parâmetro para garantir o fuso horário
            timeZone='America/Sao_Paulo'
        ).execute()
        
        # Formata as datas para exibição
        inicio = evento_criado['start'].get('dateTime')
        fim = evento_criado['end'].get('dateTime')
        
        return jsonify({
            "message": "Evento criado com sucesso!",
            "link": evento_criado['htmlLink'],
            "detalhes": {
                "id": evento_criado['id'],
                "titulo": evento_criado['summary'],
                "inicio": inicio,
                "fim": fim,
                "fuso_horario": "America/Sao_Paulo",
                "participantes": [att['email'] for att in evento_criado.get('attendees', [])]
            },
            "status": "sucesso"
        })
    
    except Exception as e:
        erro_msg = str(e)
        print(f"Erro no endpoint /criar: {erro_msg}")
        reset_service()
        return jsonify({
            "error": f"Erro ao criar evento: {erro_msg}",
            "status": "erro",
            "detalhes_erro": {
                "tipo": type(e).__name__,
                "mensagem": erro_msg
            }
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
