#!/bin/bash
# Script de inicialização para garantir que o servidor inicie rapidamente
# Render precisa detectar a porta HTTP rapidamente

# Define a porta (Render define PORT automaticamente)
PORT=${PORT:-8050}

# Inicia o gunicorn com configurações otimizadas para Render
exec gunicorn app:server \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info

