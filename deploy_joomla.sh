#!/bin/bash
# Script de deploy para integração com Joomla

echo "=== Deploy do Dashboard para Joomla ==="
echo ""

# Verifica se está em ambiente virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Ativando ambiente virtual..."
    source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
fi

# Instala dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Converte dados para Parquet (se necessário)
if [ ! -d "processed" ] || [ -z "$(ls -A processed/*.parquet 2>/dev/null)" ]; then
    echo "🔄 Convertendo dados para Parquet..."
    python convert_excel_to_parquet.py
fi

# Converte imagens para WebP (se necessário)
if [ ! -d "images/webp" ] || [ -z "$(ls -A images/webp/*.webp 2>/dev/null)" ]; then
    echo "🖼️  Convertendo imagens para WebP..."
    python convert_images_to_webp.py
fi

# Configura variáveis de ambiente
export PORT=${PORT:-8050}
export EMBED_MODE=true

echo ""
echo "✅ Deploy configurado!"
echo ""
echo "Para iniciar o servidor:"
echo "  gunicorn app:server --bind 0.0.0.0:$PORT --workers 2 --timeout 120"
echo ""
echo "Ou use a versão embed:"
echo "  gunicorn app_embed:server --bind 0.0.0.0:$PORT --workers 2 --timeout 120"
echo ""
echo "Para integrar no Joomla, use este iframe:"
echo "  <iframe src=\"http://seu-servidor:$PORT\" width=\"100%\" height=\"800px\" frameborder=\"0\"></iframe>"

