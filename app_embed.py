"""
Versão do app otimizada para embed em iframe (Joomla, WordPress, etc.)
Remove elementos desnecessários e otimiza para integração.

Uso: python app_embed.py
     ou gunicorn app_embed:server
"""
import os

# Importa o app principal
from app import app, server

# Configurações para modo embed
# Remove padding/margin para melhor integração
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }
            .dash-app {
                margin: 0;
                padding: 0;
            }
            .container-fluid {
                padding-left: 0;
                padding-right: 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    print(f"Iniciando servidor em modo embed na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

