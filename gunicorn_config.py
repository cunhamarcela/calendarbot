import os
import pathlib

# Configuração básica
bind = "0.0.0.0:10000"
workers = 2
threads = 4
worker_class = "gthread"
timeout = 120

# Garante que o diretório de dados existe
def on_starting(server):
    base_dir = pathlib.Path(__file__).parent
    data_dir = base_dir / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # Ajusta permissões se necessário
    os.chmod(data_dir, 0o755) 