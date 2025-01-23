import os
import pathlib

# Configuração básica
bind = "0.0.0.0:8000"
workers = 3
timeout = 120
worker_class = "sync"
accesslog = "-"
errorlog = "-"

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