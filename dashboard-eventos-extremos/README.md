# Dashboard Eventos Extremos - Geocalor

Dashboard leve e independente para visualização de eventos extremos.

## Características

- Mapa interativo de eventos extremos nas Regiões Metropolitanas
- Visualização HTML interativa
- Sem dependências de dados pesados

## Requisitos

- Python 3.11+
- Docker (opcional)
- Arquivo HTML: `data/mapa_interativo.html`

## Instalação Local

```bash
pip install -r requirements.txt
python app.py
```

## Executar com Docker

```bash
docker build -t dashboard-eventos-extremos .
docker run -p 8050:8050 dashboard-eventos-extremos
```
