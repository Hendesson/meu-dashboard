# Use uma imagem Python oficial como base
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Cria os diretórios necessários se não existirem
RUN mkdir -p data processed cache assets images/webp

# Expõe a porta padrão do Dash
EXPOSE 8050

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PORT=8050

# Comando para executar a aplicação
# Render define PORT automaticamente, mas usamos 8050 como fallback
# Configurações otimizadas para Render detectar a porta rapidamente:
# - 1 worker: inicia mais rápido
# - preload: carrega app antes de criar workers
# - logs diretos: para Render ver o que está acontecendo
CMD sh -c "gunicorn app:server --bind 0.0.0.0:${PORT:-8050} --workers 1 --timeout 120 --preload --access-logfile - --error-logfile - --log-level info"

