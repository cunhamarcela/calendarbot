# Comandos padrão para consulta
CONSULTAS = {
    'hoje': {
        'padroes': [
            'agenda de hoje',
            'eventos hoje',
            'compromissos hoje',
            'o que tem hoje',
            'agenda do dia',
            'agenda hoje'
        ],
        'dias': 0
    },
    'amanha': {
        'padroes': [
            'agenda de amanhã',
            'eventos amanhã',
            'compromissos amanhã',
            'o que tem amanhã',
            'agenda amanhã'
        ],
        'dias': 1
    },
    'data_especifica': {
        'padroes': [
            'agenda do dia {data}',
            'eventos do dia {data}',
            'agenda dia {data}',
            'eventos dia {data}',
            'o que tem dia {data}',
            'compromissos dia {data}',
            'agenda {data}',
            'eventos {data}',
            'o que tem {data}'
        ]
    }
}

# Padrões de consulta para outras pessoas
CONSULTA_PESSOA = [
    'agenda do {pessoa} dia {data}',
    'eventos do {pessoa} dia {data}',
    'o que o {pessoa} tem dia {data}',
    'compromissos do {pessoa} dia {data}',
    'agenda do {pessoa} {data}',
    'o que o {pessoa} tem {data}',
    'agenda do {pessoa}',
    'eventos do {pessoa}'
]

# Comandos padrão para criação
CRIACAO = {
    'padrao_simples': [
        'criar evento {titulo} dia {data} às {hora}',
        'agendar {titulo} dia {data} às {hora}',
        'marcar {titulo} dia {data} às {hora}',
        'criar {titulo} dia {data} às {hora}',
        'agendar {titulo} para {data} às {hora}'
    ],
    'padrao_local': [
        'criar evento {titulo} no {local} dia {data} às {hora}',
        'agendar {titulo} no {local} dia {data} às {hora}',
        'marcar {titulo} no {local} dia {data} às {hora}',
        'criar {titulo} no {local} dia {data} às {hora}'
    ]
}

# Comandos para eventos com outras pessoas
CRIACAO_COM_PESSOA = [
    'marcar {tipo} com {pessoa} dia {data} às {hora}',
    'agendar {tipo} com {pessoa} dia {data} às {hora}',
    'marcar {tipo} com {pessoa} {data} às {hora}',
    'agendar consulta com {pessoa} para {data} às {hora}'
]

# Comandos para verificar disponibilidade
CONSULTA_DISPONIBILIDADE = {
    'propria': [
        'horários livres dessa semana',
        'quando estou livre essa semana',
        'qual horário livre eu tenho',
        'quando posso marcar algo',
        'mostre meus horários livres'
    ],
    'outra_pessoa': [
        'horários livres do {pessoa}',
        'quando o {pessoa} está livre',
        'qual horário livre o {pessoa} tem',
        'disponibilidade do {pessoa}',
        'horários disponíveis do {pessoa}'
    ],
    'periodo': [
        'próximas semanas',
        'próximos dias',
        'essa semana',
        'semana que vem',
        'próxima semana'
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