# Configurações do Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"

# Mapeamento de pessoas e seus emails
PESSOAS = {
    'alberto': 'alberto@email.com',
    'andré': 'andre@email.com',
    # Adicione mais pessoas aqui
}

# Mapeamento de locais e endereços
LOCAIS = {
    'consultório': 'Rua Exemplo, 123',
    'pediatra': 'Av. Médico, 456',
    # Adicione mais locais aqui
}

# Duração padrão dos eventos em minutos
DURACOES = {
    'reunião': 60,
    'consulta': 60,
    'terapia': 60,
    'depilação': 120,
    'pediatra': 60,
    # Adicione mais tipos de evento aqui
}

# Horário comercial padrão
HORARIO_COMERCIAL = {
    'inicio': 9,  # 9h
    'fim': 18     # 18h
} 