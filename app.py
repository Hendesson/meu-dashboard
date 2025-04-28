import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from datetime import datetime


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Carregar dados
excel_path = "banco_dados_climaticos_consolidado (2).xlsx"

def load_data():
    df = pd.read_excel(excel_path)
    df["index"] = pd.to_datetime(df["index"], errors="coerce")
    df["isHW"] = df["isHW"].apply(lambda x: str(x).upper())
    df["year"] = df["index"].dt.year
    df["month"] = df["index"].dt.month
    return df

df = load_data()
cidades = sorted(df["cidade"].unique())
anos = sorted(df["year"].unique())

# Funções auxiliares
def calculate_anomalies(df, cidade, ano_inicio, ano_fim):
    dff = df[(df["cidade"] == cidade) & (df["year"] >= ano_inicio) & (df["year"] <= ano_fim)]
    baseline = dff["tempMed"].mean()
    df_anomalia = dff.groupby("year")["tempMed"].mean().reset_index()
    df_anomalia["anomalia"] = df_anomalia["tempMed"] - baseline
    return df_anomalia

def calculate_hw_monthly(df, cidade, ano):
    dff = df[(df["cidade"] == cidade) & (df["year"] == ano) & (df["isHW"] == "TRUE")].copy()
    dff["mes"] = dff["index"].dt.strftime("%B")  # Nome do mês em inglês
    monthly_counts = dff.groupby("mes").size().reset_index(name="frequencia")
    all_months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    monthly_counts = pd.DataFrame({"mes": all_months}).merge(
        monthly_counts, on="mes", how="left"
    ).fillna({"frequencia": 0})
    return monthly_counts

def dias_ondas_calor(df, cidade):
    return df[(df["cidade"] == cidade) & (df["isHW"] == "TRUE")]["index"].dt.date.tolist()

def prepare_heatmap_data(df):
    df_heatmap = df[df["isHW"] == "TRUE"].groupby(["cidade", "year"]).size().reset_index(name="dias_hw")
    all_combinations = pd.MultiIndex.from_product([cidades, range(1981, 2024)], names=["cidade", "year"]).to_frame(index=False)
    df_heatmap = all_combinations.merge(df_heatmap, on=["cidade", "year"], how="left").fillna({"dias_hw": 0})
    return df_heatmap

# App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard de Ondas de Calor"

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Img(src="/assets/logo.png", style={"height": "80px"}), width="auto"),
        dbc.Col(html.H2("Dashboard de Ondas de Calor", className="text-center my-4"))
    ], align="center"),

    dcc.Tabs([
        # Primeira aba: Temperaturas
        dcc.Tab(label="Temperaturas Diárias", children=[
            html.Br(),
            html.Label("Selecione o período:"),
            dcc.RangeSlider(
                id="slider-anos",
                min=min(anos),
                max=max(anos),
                step=1,
                marks={int(a): str(a) for a in anos},
                value=[min(anos), max(anos)]
            ),
            html.Br(),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Estações Meteorológicas Utilizadas")),
                        dbc.CardBody([
                            dl.Map([
                                dl.TileLayer(),
                                dl.LayerGroup([
                                    dl.Marker(position=(row["Lat"], row["Long"]),
                                              children=dl.Tooltip(row["cidade"]))
                                    for _, row in df.drop_duplicates("cidade")[["cidade", "Lat", "Long"]].iterrows()
                                ])
                            ], style={"width": "100%", "height": "400px"},
                               center=(df["Lat"].mean(), df["Long"].mean()), zoom=5),
                        ])
                    ]),
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Sobre o Projeto", className="card-title"),
                            html.P(
                                "Este dashboard foi desenvolvido para analisar e visualizar dados climáticos, com foco em ondas de calor e anomalias de temperatura. Utilizamos dados de estações meteorológicas para identificar padrões climáticos e eventos extremos, contribuindo para a conscientização e planejamento frente às mudanças climáticas.",
                                className="card-text"
                            )
                        ], style={"background-color": "#f8f9fa", "border-radius": "10px"})
                    ], className="mt-3")
                ], width=5),

                dbc.Col([
                    html.Label("Cidade:"),
                    dcc.Dropdown(cidades, cidades[0], id="cidade-temp"),
                    dcc.Loading(dcc.Graph(id="grafico-temp")),
                    dcc.Loading(dcc.Graph(id="grafico-anomalia"))
                ], width=7)
            ])
        ]),
        
        # Segunda aba: Ondas de Calor
        dcc.Tab(label="Análise de Ondas de Calor", children=[
            html.Br(),
            html.Label("Selecione a cidade e o ano para o Gráfico Polar e Calendário:"),
            dbc.Row([
                dbc.Col(dcc.Dropdown(id="cidade-hw", options=[{"label": cidade, "value": cidade} for cidade in cidades], value=cidades[0]), width=6),
                dbc.Col(dcc.Dropdown(id="ano-hw", options=[{"label": str(ano), "value": ano} for ano in anos], value=anos[-1]), width=6)
            ]),
            html.Br(),

            dbc.Row([
                dbc.Col([
                    dcc.Loading(dcc.Graph(id="heatmap-hw"))
                ], width=6),
                dbc.Col([
                    dcc.Loading(dcc.Graph(id="grafico-polar"))
                ], width=6)
            ]),

            html.Br(),
            html.H5("Calendário de Ondas de Calor:", className="text-center"),
            html.Div([
                dcc.Loading(dcc.DatePickerRange(
                    id="calendario-hw",
                    display_format="DD/MM/YYYY",
                    min_date_allowed=min(df["index"]).date(),
                    max_date_allowed=max(df["index"]).date(),
                    start_date_placeholder_text="Início",
                    end_date_placeholder_text="Fim"
                ))
            ], style={"text-align": "center"})
        ])
    ])
], fluid=True)

# Callbacks
@app.callback(
    [Output("grafico-temp", "figure"),
     Output("grafico-anomalia", "figure")],
    [Input("cidade-temp", "value"),
     Input("slider-anos", "value")]
)
def update_temp(cidade, anos_selecionados):
    ano_inicio, ano_fim = anos_selecionados
    dff = df[(df["cidade"] == cidade) & (df["year"] >= ano_inicio) & (df["year"] <= ano_fim)]

    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=dff["index"], y=dff["tempMax"], name="Máxima", line=dict(color="red")))
    fig_temp.add_trace(go.Scatter(x=dff["index"], y=dff["tempMed"], name="Média", line=dict(color="blue")))
    fig_temp.add_trace(go.Scatter(x=dff["index"], y=dff["tempMin"], name="Mínima", line=dict(color="green")))
    fig_temp.update_layout(
        title=f"Temperaturas em {cidade} ({ano_inicio}-{ano_fim})",
        xaxis_title="Data",
        yaxis_title="Temperatura (°C)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12)
    )

    df_anomalia = calculate_anomalies(df, cidade, ano_inicio, ano_fim)
    fig_anomalia = px.scatter(
        df_anomalia, x="year", y="anomalia", size=np.abs(df_anomalia["anomalia"]),
        title=f"Anomalias de Temperatura Média - {cidade} ({ano_inicio}-{ano_fim})",
        labels={"anomalia": "Anomalia (°C)"}
    )
    fig_anomalia.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12)
    )
    return fig_temp, fig_anomalia

@app.callback(
    [Output("heatmap-hw", "figure"),
     Output("grafico-polar", "figure"),
     Output("calendario-hw", "start_date"),
     Output("calendario-hw", "end_date"),
     Output("calendario-hw", "min_date_allowed"),
     Output("calendario-hw", "max_date_allowed")],
    [Input("cidade-hw", "value"),
     Input("ano-hw", "value")]
)
def update_hw(cidade, ano_polar):
    # Heatmap
    df_heatmap = prepare_heatmap_data(df)
    max_dias_hw = max(df_heatmap["dias_hw"], default=1)
    
    heatmap_fig = px.density_heatmap(
        df_heatmap,
        x="year",
        y="cidade",
        z="dias_hw",
        color_continuous_scale="OrRd",
        labels={"dias_hw": "Dias de Onda de Calor"},
        title="Total de Dias de Onda de Calor por Cidade e Ano (1981-2023)"
    )
    heatmap_fig.update_layout(
        xaxis=dict(
            title="Ano",
            tickangle=45,
            tickfont=dict(size=10),
            tickmode="linear",
            dtick=1,
            gridcolor="rgba(0,0,0,0.1)"
        ),
        yaxis=dict(
            title="Cidade",
            tickfont=dict(size=10),
            automargin=True
        ),
        coloraxis_colorbar=dict(
            title=dict(text="Dias de Onda de Calor", font=dict(size=14)),
            tickfont=dict(size=12)
        ),
        height=600,
        margin=dict(l=150, r=50, t=100, b=100),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        hovermode="closest",
        hoverlabel=dict(font_size=12)
    )

    # Polar plot
    df_polar = calculate_hw_monthly(df, cidade, ano_polar)
    
    fig_polar = go.Figure()
    fig_polar.add_trace(go.Scatterpolar(
        r=df_polar["frequencia"],
        theta=df_polar["mes"],
        fill="toself",
        mode="lines+markers",
        line=dict(color="blue", width=2),
        marker=dict(color="blue", size=8),
        name="Frequência"
    ))
    fig_polar.update_layout(
        title=f"Frequência de Ondas de Calor em {cidade} - {ano_polar}",
        polar=dict(
            radialaxis=dict(visible=True, tickfont=dict(size=10)),
            angularaxis=dict(direction="clockwise", tickfont=dict(size=10))
        ),
        showlegend=False,
        height=400,
        margin=dict(l=50, r=50, t=100, b=50),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12)
    )

    # Calendário
    dias_calor = dias_ondas_calor(df, cidade)
    if dias_calor:
        min_date = min(dias_calor)
        max_date = max(dias_calor)
    else:
        min_date = min(df["index"]).date()
        max_date = max(df["index"]).date()
    
    return heatmap_fig, fig_polar, min_date, max_date, min_date, max_date

# Rodar App
# Rodar App com Gunicorn (não use app.run() em produção)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use a porta do ambiente ou 5000 como padrão
    app.run(host='0.0.0.0', port=port, debug=False)

