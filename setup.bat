@echo off
echo Criando ambiente virtual...
python -m venv .venv

echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo Instalando dependências...
python -m pip install --upgrade pip
python -m pip install flask
python -m pip install google-auth-oauthlib
python -m pip install google-api-python-client
python -m pip install python-dateutil
python -m pip install pytz
python -m pip install python-dotenv

echo Configuração concluída!
echo Para rodar o servidor, use: python main.py 