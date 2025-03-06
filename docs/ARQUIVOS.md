# Documentação dos Arquivos Principais

## prompts.py
Contém todos os padrões de comando que o bot reconhece:
- Padrões para consultas de agenda
- Padrões para verificar disponibilidade
- Padrões para criar eventos
- Exemplos de uso para o usuário

## config.py
Arquivo de configuração com:
- Credenciais do Google Calendar
- Mapeamento de pessoas e seus emails
- Locais padrão e endereços
- Durações padrão de eventos
- Configurações de horário comercial

## main.py
Arquivo principal da aplicação:
- Configuração do Flask
- Rotas da API
- Gerenciamento de autenticação
- Integração com Google Calendar
- Processamento de requisições

## gunicorn_config.py
Configurações do servidor Gunicorn:
- Número de workers
- Timeout
- Configurações de log
- Diretórios de dados

## requirements.txt
Lista de dependências do projeto:
- Flask para o servidor web
- Bibliotecas do Google para Calendar API
- Utilitários de data e hora
- Outras dependências necessárias 