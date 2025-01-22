# Comandos padrão para consulta
CONSULTAS = {
    'hoje': {
        'padroes': [
            'o que tem hoje',
            'agenda hoje',
            'eventos hoje',
            'compromissos hoje'
        ],
        'dias': 0
    },
    'amanha': {
        'padroes': [
            'o que tem amanhã',
            'agenda amanhã',
            'eventos amanhã',
            'compromissos amanhã'
        ],
        'dias': 1
    },
    'data_especifica': {
        'padroes': [
            'o que tem dia {data}',
            'agenda dia {data}',
            'eventos dia {data}',
            'compromissos dia {data}'
        ]
    }
}

# Padrões de consulta para outras pessoas
CONSULTA_PESSOA = [
    'o que o {pessoa} tem hoje',
    'o que o {pessoa} tem amanhã',
    'o que o {pessoa} tem dia {data}',
    'agenda do {pessoa} hoje',
    'agenda do {pessoa} amanhã',
    'agenda do {pessoa} dia {data}'
]

# Padrões de disponibilidade
DISPONIBILIDADE = {
    'propria': [
        'quando estou livre',
        'meus horários livres',
        'quais horários tenho livre',
        'quando posso marcar algo'
    ],
    'outra_pessoa': [
        'quando o {pessoa} está livre',
        'horários livres do {pessoa}',
        'quando o {pessoa} pode',
        'disponibilidade do {pessoa}'
    ],
    'periodo': [
        'essa semana',
        'próxima semana',
        'semana que vem',
        'próximas semanas',
        'próximos dias'
    ]
}

# Comandos para criação de eventos
CRIACAO = {
    'simples': [
        'marcar {tipo} dia {data} às {hora}',
        'agendar {tipo} dia {data} às {hora}',
        'criar {tipo} dia {data} às {hora}'
    ],
    'com_pessoa': [
        'marcar {tipo} com {pessoa} dia {data} às {hora}',
        'agendar {tipo} com {pessoa} dia {data} às {hora}',
        'criar {tipo} com {pessoa} dia {data} às {hora}'
    ]
}

# Eventos recorrentes
EVENTOS_RECORRENTES = {
    'terapia': {
        'duracao': 60,
        'recorrencia': 'WEEKLY',
        'local': None
    },
    'pediatra': {
        'duracao': 60,
        'recorrencia': None,
        'local': 'pediatra'
    }
}

# Exemplos de uso para o usuário
EXEMPLOS_USO = """
Comandos disponíveis:

Consultas:
- agenda de hoje
- eventos amanhã
- agenda dia 25/02/2025
- o que tem hoje
- compromissos amanhã
- o que tem dia 25/02

Consultas de outras pessoas:
- agenda do alberto dia 25/02/2025
- o que o alberto tem amanhã
- eventos do alberto hoje

Verificar disponibilidade:
- qual horário livre eu tenho essa semana
- horários livres do alberto nas próximas semanas
- quando estou livre essa semana

Criação:
- criar evento reunião dia 25/02/2025 às 15:00
- agendar depilação no consultório dia 26/02 às 14:30
- marcar consulta no pediatra amanhã às 10:00
- marcar pediatra com o andré dia 04/02/2025 às 16:00
- marcar terapia 24/01 às 16:00
"""

# Formatos de data aceitos
FORMATOS_DATA = [
    'DD/MM/YYYY',
    'DD/MM',
    'hoje',
    'amanhã'
]

# Mensagens de erro padronizadas
ERROS = {
    'data_invalida': 'Por favor, use o formato DD/MM/YYYY ou DD/MM (exemplo: 25/02/2025 ou 25/02)',
    'hora_invalida': 'Por favor, use o formato HH:MM (exemplo: 15:00)',
    'comando_invalido': f'Comando não reconhecido. Use um dos formatos:\n{EXEMPLOS_USO}',
    'acesso_negado': 'Não tenho acesso à agenda desta pessoa',
    'sem_eventos': 'Nenhum evento encontrado para esta data'
} 