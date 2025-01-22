from flask import Flask, request, jsonify, render_template
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Necessário para desenvolvimento local
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# Escopos necessários para acessar a Google Agenda
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Serviço de autenticação global
service = None

# Função para autenticar na Google API
def autenticar():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 
        SCOPES,
        redirect_uri='http://localhost:8080/oauth2callback'
    )
    creds = flow.run_local_server(
        port=8080,
        access_type='offline',
        include_granted_scopes=True
    )
    return build('calendar', 'v3', credentials=creds)

# Rota inicial
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint para listar eventos
@app.route('/listar', methods=['GET'])
def listar_eventos():
    global service
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

# Endpoint para criar um evento
@app.route('/criar', methods=['POST'])
def criar_evento():
    global service
    data = request.json
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

if __name__ == '__main__':
    # Primeiro, autentica no Google
    service = autenticar()
    
    print("Servidor rodando em http://localhost:8080")
    # Inicia o Flask na porta 8080
    app.run(host='0.0.0.0', port=8080, debug=True)
