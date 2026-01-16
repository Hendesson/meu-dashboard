"""
Dashboard Eventos Extremos - Geocalor
Versão leve e independente para visualização de eventos extremos
"""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
    ]
)
server = app.server
app.title = "Dashboard de Ondas de Calor - Eventos Extremos"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def _load_map_html() -> str:
    """Carrega o conteúdo do mapa interativo HTML."""
    map_path = os.path.join(BASE_DIR, 'mapa_interativo.html')
    if os.path.exists(map_path):
        try:
            with open(map_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Erro ao ler mapa: {e}")
    
    map_path = os.path.join(DATA_DIR, 'mapa_interativo.html')
    if os.path.exists(map_path):
        try:
            with open(map_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Erro ao ler mapa de data/: {e}")
    
    logger.warning("mapa_interativo.html não encontrado")
    return '<html><body><p>Mapa não disponível</p></body></html>'

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Img(src=app.get_asset_url('geocalor.png'), className="logo-img"),
            html.H2("Dashboard de Ondas de Calor - Eventos Extremos", className="text-center my-4")
        ], width=12)
    ], align="center"),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Mapa interativo dos eventos extremos nas Regiões Metropolitanas", className="text-center")),
                dbc.CardBody([
                    html.Div([
                        html.Iframe(
                            id="mapa-interativo",
                            srcDoc=_load_map_html(),
                            style={
                                'width': '100%',
                                'height': '600px',
                                'border': 'none'
                            }
                        )
                    ])
                ])
            ])
        ], width=12)
    ])
], fluid=True)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
