from datetime import datetime, timedelta
import re
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta
from config import PESSOAS, LOCAIS, DURACOES, HORARIO_COMERCIAL

def extrair_data_hora(texto):
    """Extrai data e hora do texto"""
    texto = texto.lower()
    agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
    
    # Padrões de data/hora
    padrao_data_hora = {
        r'hoje[^\d]*(\d{1,2})[h:]?(\d{2})?\s*': lambda m: agora.replace(
            hour=int(m.group(1)), 
            minute=int(m.group(2)) if m.group(2) else 0
        ),
        r'amanhã[^\d]*(\d{1,2})[h:]?(\d{2})?\s*': lambda m: (agora + timedelta(days=1)).replace(
            hour=int(m.group(1)), 
            minute=int(m.group(2)) if m.group(2) else 0
        ),
        r'(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\s+(?:as\s+)?(\d{1,2})[h:]?(\d{2})?\s*': lambda m: agora.replace(
            day=int(m.group(1)),
            month=int(m.group(2)),
            year=int(m.group(3)) if m.group(3) else agora.year,
            hour=int(m.group(4)),
            minute=int(m.group(5)) if m.group(5) else 0
        ),
        r'próxima\s+(\w+)(?:\s+[àa]s?\s+(\d{1,2})[h:]?(\d{2})?)?\s*': lambda m: calcular_proximo_dia(
            m.group(1),
            int(m.group(2)) if m.group(2) else 9,
            int(m.group(3)) if m.group(3) else 0
        )
    }
    
    for padrao, func in padrao_data_hora.items():
        match = re.search(padrao, texto)
        if match:
            return func(match)
    
    return None

def calcular_proximo_dia(dia_semana, hora=9, minuto=0):
    """Calcula a próxima ocorrência de um dia da semana"""
    dias = {
        'segunda': 0, 'segunda-feira': 0,
        'terça': 1, 'terca': 1, 'terça-feira': 1,
        'quarta': 2, 'quarta-feira': 2,
        'quinta': 3, 'quinta-feira': 3,
        'sexta': 4, 'sexta-feira': 4,
        'sábado': 5, 'sabado': 5,
        'domingo': 6
    }
    
    if dia_semana.lower() not in dias:
        return None
        
    agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
    dia_alvo = dias[dia_semana.lower()]
    dias_adicionar = (dia_alvo - agora.weekday() + 7) % 7
    if dias_adicionar == 0:
        dias_adicionar = 7
        
    data = agora + timedelta(days=dias_adicionar)
    return data.replace(hour=hora, minute=minuto)

def extrair_email(texto):
    """Extrai email ou nome de pessoa do texto"""
    texto = texto.lower()
    
    # Primeiro tenta encontrar um email direto
    match_email = re.search(r'[\w\.-]+@[\w\.-]+', texto)
    if match_email:
        return match_email.group(0)
    
    # Depois procura por nomes no mapeamento
    for nome, email in PESSOAS.items():
        if nome in texto:
            return email
    
    # Por fim, tenta extrair um nome e converter para email
    padroes = [
        r'(?:agenda|eventos|compromissos)\s+(?:do|da|de)\s+([^,\s]+(?:\s+[^,\s]+){0,2})',
        r'(?:o que|quais|qual)\s+(?:o|a)\s+([^,\s]+(?:\s+[^,\s]+){0,2})\s+tem',
        r'([^,\s]+(?:\s+[^,\s]+){0,2})\s+(?:está livre|tem algum evento|tem compromisso)'
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            nome = match.group(1).strip()
            return PESSOAS.get(nome.lower(), f"{nome.replace(' ', '.').lower()}@gmail.com")
    
    return 'primary'

def sugerir_horario(service, data, duracao=60):
    """Sugere próximo horário livre"""
    inicio_dia = data.replace(
        hour=HORARIO_COMERCIAL['inicio'],
        minute=0, second=0
    )
    fim_dia = data.replace(
        hour=HORARIO_COMERCIAL['fim'],
        minute=0, second=0
    )
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=inicio_dia.isoformat(),
        timeMax=fim_dia.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    horarios_ocupados = [
        (parser.parse(event['start'].get('dateTime')),
         parser.parse(event['end'].get('dateTime')))
        for event in events_result.get('items', [])
    ]
    
    horario_atual = inicio_dia
    while horario_atual < fim_dia:
        # Verifica se o horário está livre
        livre = True
        for inicio, fim in horarios_ocupados:
            if (horario_atual >= inicio and 
                horario_atual < fim):
                livre = False
                horario_atual = fim
                break
        
        if livre:
            # Verifica se cabe o evento
            fim_evento = horario_atual + timedelta(minutes=duracao)
            if fim_evento <= fim_dia:
                return horario_atual
            
        horario_atual += timedelta(minutes=30)
    
    return None

def processar_comando(texto, service):
    """Processa comandos em linguagem natural"""
    texto = texto.lower()
    
    try:
        # Verifica se é um comando de criação
        if any(palavra in texto for palavra in ['crie', 'agende', 'marque', 'criar', 'agendar', 'marcar']):
            # Extrai título do evento
            match_titulo = re.search(r'chamado\s+(.+?)(?:\s+(?:dia|às|as|no dia|em|para)|$)', texto)
            if not match_titulo:
                match_titulo = re.search(r'(?:crie|agende|marque)\s+(?:uma|um)?\s*(.+?)(?:\s+(?:dia|às|as|no dia|em|para)|$)', texto)
            
            if not match_titulo:
                return {
                    "status": "erro",
                    "mensagem": "Não consegui entender o título do evento"
                }
            
            titulo = match_titulo.group(1).strip()
            data_hora = extrair_data_hora(texto)
            
            if not data_hora:
                return {
                    "status": "erro",
                    "mensagem": "Não consegui entender a data e hora do evento"
                }
            
            # Adiciona sugestão de horário se não especificado
            if not data_hora:
                data = datetime.now(pytz.timezone('America/Sao_Paulo'))
                if 'amanhã' in texto:
                    data += timedelta(days=1)
                
                # Determina duração baseado no tipo de evento
                duracao = 60
                for tipo, dur in DURACOES.items():
                    if tipo in texto:
                        duracao = dur
                        break
                
                data_hora = sugerir_horario(service, data, duracao)
                if not data_hora:
                    return {
                        "status": "erro",
                        "mensagem": "Não encontrei horários livres para hoje/amanhã. Tente especificar outra data."
                    }
            
            # Identifica local do evento
            local = None
            for nome_local, endereco in LOCAIS.items():
                if nome_local in texto:
                    local = endereco
                    break
            
            # Cria o evento
            evento = {
                'summary': titulo,
                'location': local,
                'start': {
                    'dateTime': data_hora.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': (data_hora + timedelta(minutes=duracao)).isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                }
            }
            
            evento_criado = service.events().insert(
                calendarId='primary',
                body=evento
            ).execute()
            
            return {
                "status": "sucesso",
                "mensagem": f"Evento '{titulo}' criado para {data_hora.strftime('%d/%m/%Y às %H:%M')}",
                "link": evento_criado['htmlLink']
            }
            
        # Verifica se é um comando de consulta
        elif any(palavra in texto for palavra in ['mostre', 'liste', 'quais', 'tem', 'há', 'consulte', 'livre']):
            # Extrai a data do comando
            data = extrair_data_hora(texto)
            if not data:
                # Se não encontrou data específica, assume hoje
                data = datetime.now(pytz.timezone('America/Sao_Paulo'))
            
            # Ajusta para início e fim do dia especificado
            inicio = data.replace(hour=0, minute=0, second=0, microsecond=0)
            fim = data.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Extrai email/calendário a ser consultado
            calendar_id = extrair_email(texto)
            
            try:
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=inicio.isoformat(),  # Usa a data extraída do comando
                    timeMax=fim.isoformat(),     # Usa a data extraída do comando
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                
                if not events:
                    nome_agenda = "sua agenda" if calendar_id == 'primary' else f"agenda de {calendar_id.split('@')[0]}"
                    return {
                        "status": "sucesso",
                        "mensagem": f"Nenhum evento encontrado em {nome_agenda} para {data.strftime('%d/%m/%Y')}"
                    }
                
                eventos_formatados = []
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    start_time = parser.parse(start).strftime('%H:%M')
                    eventos_formatados.append(f"- {start_time}: {event['summary']}")
                
                nome_agenda = "sua agenda" if calendar_id == 'primary' else f"agenda de {calendar_id.split('@')[0]}"
                return {
                    "status": "sucesso",
                    "mensagem": f"Eventos em {nome_agenda} para {data.strftime('%d/%m/%Y')}:\n" + "\n".join(eventos_formatados)
                }
                
            except Exception as e:
                if 'Not Found' in str(e):
                    return {
                        "status": "erro",
                        "mensagem": f"Não tenho acesso à agenda de {calendar_id}"
                    }
                raise e
            
        else:
            return {
                "status": "erro",
                "mensagem": "Desculpe, não entendi o comando. Tente algo como:\n" +
                          "- crie uma reunião amanhã às 15h\n" +
                          "- mostre meus eventos de hoje\n" +
                          "- o que Alberto tem na agenda amanhã?"
            }
            
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao processar comando: {str(e)}"
        } 