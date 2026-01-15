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

# Copia e torna executável o script de inicialização
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expõe a porta padrão do Dash
EXPOSE 8050

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PORT=8050

# Comando para executar a aplicação usando o script de inicialização
# O script garante que o servidor inicie rapidamente para o Render detectar a porta
CMD ["/start.sh"]

