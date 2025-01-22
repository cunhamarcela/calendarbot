#!/bin/bash

# Cria e configura o diretório de dados
mkdir -p /opt/render/project/src/data
chmod 755 /opt/render/project/src/data

# Copia o arquivo de credenciais para o diretório de dados
cp credentials.json /opt/render/project/src/data/

# Inicia o Gunicorn
gunicorn main:app --config gunicorn_config.py 