from flask import Flask, request, jsonify, render_template
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Configurações de ambiente
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# Escopos necessários para acessar a Google Agenda
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Serviço de autenticação global
service = None

# Função para autenticar na Google API
def autenticar():
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',
            SCOPES,
            redirect_uri=os.environ.get('REDIRECT_URI', 'http://localhost:8080/oauth2callback')
        )
        # Use run_console() para ambientes de produção
        creds = flow.run_console()
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"Erro ao autenticar: {e}")
        raise e

# Inicializa o serviço na primeira requisição
@app.before_first_request
def initialize_service():
    global service
    if service is None:
        service = autenticar()

# Rota inicial
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint para listar eventos
@app.route('/listar', methods=['GET'])
def listar_eventos():
    global service
    try:
        events_result = service.events().list(
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
        return jsonify({"error": str(e)}), 500

# Endpoint para criar um evento
@app.route('/criar', methods=['POST'])
def criar_evento():
    global service
    try:
        data = request.json

        # Validar dados recebidos
        if not all(k in data for k in ("summary", "location", "start", "end", "attendees")):
            return jsonify({"error": "Dados incompletos na requisição"}), 400

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

        evento_criado = service.events().insert(calendarId='primary', body=evento).execute()
        return jsonify({"message": "Evento criado!", "link": evento_criado['htmlLink']})
    
    except Exception as e:
        print(f"Erro no endpoint /criar: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Para desenvolvimento local
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
