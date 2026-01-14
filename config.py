import os
from typing import Dict, Any

# Configurações do app
APP_CONFIG: Dict[str, Any] = {
    "title": "Dashboard de Ondas de Calor",
    "theme": "BOOTSTRAP",
    "port": int(os.environ.get("PORT", 8050)),
    "host": "0.0.0.0",
    "debug": False
}

# Configurações de dados
DATA_CONFIG: Dict[str, Any] = {
    "data_file": "banco_dados_climaticos_consolidado (2).xlsx"
}

# Configurações de visualização
VISUALIZATION_CONFIG: Dict[str, Any] = {
    "colors": {
        "temp_max": "red",
        "temp_med": "blue",
        "temp_min": "green",
        "polar": "blue"
    },
    "layout": {
        "plot_bgcolor": "white",
        "paper_bgcolor": "white",
        "font_size": 12,
        "margin": {
            "l": 50,
            "r": 50,
            "t": 100,
            "b": 50
        }
    },
    "heatmap": {
        "color_scale": "OrRd",
        "height": 600,
        "margin": {
            "l": 150,
            "r": 50,
            "t": 100,
            "b": 100
        }
    },
    "polar": {
        "height": 400,
        "line_width": 2,
        "marker_size": 8
    }
}

# Configurações do mapa
MAP_CONFIG: Dict[str, Any] = {
    "default_center": (-15, -50),
    "default_zoom": 5,
    "style": {
        "width": "100%",
        "height": "400px"
    }
}

# Configurações de datas
DATE_CONFIG: Dict[str, Any] = {
    "min_year": 1981,
    "max_year": 2023,
    "date_format": "DD/MM/YYYY"
} 