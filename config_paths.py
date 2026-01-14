"""
Configuração de caminhos para compatibilidade Windows/Linux.
Usa caminhos relativos baseados no diretório do projeto.
"""
import os

# Diretório base do projeto (onde está app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretório de dados
DATA_DIR = os.path.join(BASE_DIR, "data")

# Diretório de dados processados
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")

# Diretório de cache
CACHE_DIR = os.path.join(BASE_DIR, "cache")

# Diretório de assets
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Diretório de imagens WebP
IMAGES_WEBP_DIR = os.path.join(BASE_DIR, "images", "webp")

# Cria diretórios se não existirem
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(IMAGES_WEBP_DIR, exist_ok=True)

