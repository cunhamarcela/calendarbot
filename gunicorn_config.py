import os
import pathlib

# Configuração básica
bind = "0.0.0.0:10000"
workers = 2
threads = 4
worker_class = "gthread"
timeout = 120

# Configuração de diretórios
data_dir = "/opt/render/project/src/data"

def on_starting(server):
    """Configuração inicial do servidor"""
    # Cria diretório de dados se não existir
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, mode=0o755)
    else:
        os.chmod(data_dir, 0o755)
    
    print(f"Diretório de dados configurado em: {data_dir}") 