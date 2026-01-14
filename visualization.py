import plotly.express as px
import plotly.graph_objs as go
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np

class Visualizer:
    def __init__(self):
        """Inicializa o visualizador."""
        pass

    def create_temperature_plot(
        self,
        df: pd.DataFrame,
        cidade: str,
        ano_inicio: int,
        ano_fim: int
    ) -> go.Figure:
        """
        Cria o gráfico de temperaturas.
        
        Args:
            df: DataFrame com os dados
            cidade: Nome da cidade
            ano_inicio: Ano inicial
            ano_fim: Ano final
            
        Returns:
            Figura do Plotly
        """
        if df.empty:
            return go.Figure()
            
        dff = df[
            (df["cidade"] == cidade) & 
            (df["year"] >= ano_inicio) & 
            (df["year"] <= ano_fim)
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dff["index"],
            y=dff["tempMax"],
            name="Máxima",
            line=dict(color="red")
        ))
        fig.add_trace(go.Scatter(
            x=dff["index"],
            y=dff["tempMed"],
            name="Média",
            line=dict(color="yellow")
        ))
        fig.add_trace(go.Scatter(
            x=dff["index"],
            y=dff["tempMin"],
            name="Mínima",
            line=dict(color="blue")
        ))
        
        fig.update_layout(
            title=f"Temperaturas em {cidade} ({ano_inicio}-{ano_fim})",
            xaxis_title="Data",
            yaxis_title="Temperatura (°C)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=12),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

    def create_heatmap(
        self,
        df_heatmap: pd.DataFrame
    ) -> go.Figure:
        """
        Cria o heatmap de ondas de calor.
        
        Args:
            df_heatmap: DataFrame com os dados do heatmap
            
        Returns:
            Figura do Plotly
        """
        if df_heatmap.empty:
            return go.Figure()
            
        fig = px.density_heatmap(
            df_heatmap,
            x="year",
            y="cidade",
            z="dias_hw",
            color_continuous_scale="OrRd",
            labels={"dias_hw": "Dias de Onda de Calor"},
            title=f"Total de Dias de Onda de Calor por Cidade e Ano ({df_heatmap['year'].min()}-{df_heatmap['year'].max()})"
        )
        
        fig.update_layout(
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
        
        return fig

    def create_polar_plot(
        self,
        df_polar: pd.DataFrame,
        cidade: str,
        ano: Optional[int]
    ) -> go.Figure:
        """
        Cria o gráfico polar de frequência mensal.
        
        Args:
            df_polar: DataFrame com os dados mensais
            cidade: Nome da cidade
            ano: Ano de análise (None para todos os anos)
            
        Returns:
            Figura do Plotly
        """
        if df_polar.empty or df_polar["frequencia"].sum() == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhuma onda de calor registrada para esta cidade/ano",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return fig
            
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=df_polar["frequencia"],
            theta=df_polar["mes"],
            fill="toself",
            mode="lines+markers",
            line=dict(color="blue", width=2),
            marker=dict(color="blue", size=8),
            name="Frequência"
        ))
        
        title = f"Frequência de Ondas de Calor em {cidade}"
        if ano is not None:
            title += f" - {ano}"
        else:
            title += " (Todos os anos)"
            
        fig.update_layout(
            title=title,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    tickfont=dict(size=10),
                    gridcolor="rgba(0,0,0,0.1)"
                ),
                angularaxis=dict(
                    direction="clockwise",
                    tickfont=dict(size=10)
                )
            ),
            showlegend=False,
            height=400,
            margin=dict(l=50, r=50, t=100, b=50),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=12)
        )
        
        return fig 

    def create_umidity_plot(
        self,
        df: pd.DataFrame,
        cidade: str,
        ano_inicio: int,
        ano_fim: int
    ) -> go.Figure:
        """
        Cria o gráfico de umidades médias mensais.
        
        Args:
            df: DataFrame com os dados
            cidade: Nome da cidade
            ano_inicio: Ano inicial
            ano_fim: Ano final
            
        Returns:
            Figura do Plotly
        """
        if df.empty:
            return go.Figure()
            
        dff = df[
            (df["cidade"] == cidade) & 
            (df["year"] >= ano_inicio) & 
            (df["year"] <= ano_fim)
        ]
        
        # Calcula a média mensal de umidade
        monthly_umidity = dff.groupby(dff["index"].dt.month)["HumidadeMed"].mean().reset_index()
        monthly_umidity["mes"] = monthly_umidity["index"].map({
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_umidity["mes"],
            y=monthly_umidity["HumidadeMed"],
            name="Umidade Média",
            line=dict(color="rgb(0, 128, 255)")
        ))
        
        fig.update_layout(
            title=f"Umidade Média Mensal em {cidade} ({ano_inicio}-{ano_fim})",
            xaxis_title="Mês",
            yaxis_title="Umidade Relativa (%)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=12),
            hovermode="x unified",
            xaxis=dict(
                categoryorder="array",
                categoryarray=[
                    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
                ]
            )
        )
        
        return fig
        
    def create_temperature_hw_plot(
        self,
        df: pd.DataFrame,
        cidade: str,
        ano: int
    ) -> go.Figure:
        """
        Cria o gráfico de temperaturas com indicadores de ondas de calor e picos.
        
        Args:
            df: DataFrame com os dados
            cidade: Nome da cidade
            ano: Ano de análise
            
        Returns:
            Figura do Plotly
        """
        if df.empty:
            return go.Figure()
            
        dff = df[
            (df["cidade"] == cidade) &
            (df["year"] == ano)
        ].copy()
        
        # Garante que 'index' é datetime para plotagem
        dff['index'] = pd.to_datetime(dff['index'])
        
        fig = go.Figure()
        
        # Adiciona traces de temperatura
        fig.add_trace(go.Scatter(
            x=dff["index"],
            y=dff["tempMax"],
            mode='lines+markers',
            name="Máxima",
            line=dict(color="red"),
            marker=dict(size=4)
        ))
        fig.add_trace(go.Scatter(
            x=dff["index"],
            y=dff["tempMed"],
            mode='lines+markers',
            name="Média",
            line=dict(color="orange"),
            marker=dict(size=4)
        ))
        fig.add_trace(go.Scatter(
            x=dff["index"],
            y=dff["tempMin"],
            mode='lines+markers',
            name="Mínima",
            line=dict(color="blue"),
            marker=dict(size=4)
        ))
        
        # Mapeamento de intensidade para cor (transparência ou tonalidade de laranja)
        # Vamos usar a intensidade para ajustar a opacidade ou brilho do retângulo
        def get_hw_color_intensity(intensity):
            intensity_map = {
                "low-intensity": 0.4,  # Mais transparente
                "severe": 0.6,       # Médio
                "extreme": 0.8       # Menos transparente/Mais opaco
            }
            return intensity_map.get(str(intensity).strip().lower(), 0.3) # Default para opacidade baixa
        
        # Adiciona formas para dias de onda de calor
        shapes = []
        for index, row in dff.iterrows():
            # Verifica se 'isHW' existe e é tratado como booleano (True/False)
            # Ou se a coluna existe e o valor indica onda de calor (ex: 'VERDADEIRO', 'TRUE', 1)
            # Adicionando uma verificação robusta para o campo isHW
            is_hw_day = False
            if 'isHW' in row and pd.notna(row['isHW']):
                 # Trata diferentes representações de True
                 is_hw_day = str(row['isHW']).strip().upper() in ['VERDADEIRO', 'TRUE', '1']
            
            if is_hw_day:
                opacity = get_hw_color_intensity(row.get('HW_Intensity', 'low-intensity')) # Usa HW_Intensity para cor
                shapes.append({
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': row['index'] - pd.Timedelta(days=0.5), # Ajusta para cobrir o dia
                    'x1': row['index'] + pd.Timedelta(days=0.5), # Ajusta para cobrir o dia
                    'y0': 0,
                    'y1': 1,
                    'fillcolor': 'orange',
                    'opacity': opacity,
                    'line': dict(width=0),
                    'layer': 'below'
                })
                
        # Identifica picos de temperatura (exemplo simples: temperatura máxima acima do 90º percentil)
        # Você pode ajustar esta lógica conforme necessário
        high_temp_threshold = dff['tempMax'].quantile(0.95) if not dff['tempMax'].empty else None
        peak_annotations = []
        
        if high_temp_threshold is not None:
             for index, row in dff.iterrows():
                 if row['tempMax'] >= high_temp_threshold:
                     peak_annotations.append({
                         'x': row['index'],
                         'y': row['tempMax'],
                         'xref': 'x',
                         'yref': 'y',
                         'text': 'Pico',
                         'showarrow': True,
                         'arrowhead': 2,
                         'ax': 0,
                         'ay': -40,
                         'bgcolor': 'rgba(255, 68, 68, 0.8)',
                         'bordercolor': '#c23232',
                         'borderwidth': 1,
                         'borderpad': 4,
                         'opacity': 0.9,
                         'font': dict(color='white', size=10)
                     })

        # Adiciona anotações para dias de onda de calor (Label Anchors)
        # Vamos adicionar o HWDay_Intensity acima do retângulo laranja
        hw_day_annotations = []
        for index, row in dff.iterrows():
             is_hw_day = False
             if 'isHW' in row and pd.notna(row['isHW']):
                  is_hw_day = str(row['isHW']).strip().upper() in ['VERDADEIRO', 'TRUE', '1']

             if is_hw_day and 'HWDay_Intensity' in row and pd.notna(row['HWDay_Intensity']):
                  hw_day_annotations.append({
                      'x': row['index'],
                      'y': 1.02, # Posição acima do gráfico (em "paper" coordinates)
                      'xref': 'x',
                      'yref': 'paper',
                      'text': str(row['HWDay_Intensity']), # Texto com a intensidade do dia
                      'showarrow': False,
                      'bgcolor': 'rgba(255, 165, 0, 0.6)', # Cor de fundo semi-transparente
                      'bordercolor': 'orange',
                      'borderwidth': 1,
                      'borderpad': 2,
                      'font': dict(color='white', size=9),
                      'textangle': 0, # Ângulo do texto
                      'xanchor': 'center',
                      'yanchor': 'bottom'
                  })

        fig.update_layout(
            title=f"Temperaturas Diárias e Ondas de Calor em {cidade} - {ano}",
            xaxis_title="Data",
            yaxis_title="Temperatura (°C)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=12),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            shapes=shapes,
            annotations=peak_annotations + hw_day_annotations # Combina as anotações de pico e de HWDay_Intensity
        )
        
        return fig

    def create_umidity_hw_plot(
        self,
        df: pd.DataFrame,
        cidade: str,
        ano: int
    ) -> go.Figure:
        """
        Cria o gráfico de umidade com indicadores de ondas de calor.
        
        Args:
            df: DataFrame com os dados
            cidade: Nome da cidade
            ano: Ano de análise
            
        Returns:
            Figura do Plotly
        """
        if df.empty:
            return go.Figure()
            
        dff = df[
            (df["cidade"] == cidade) &
            (df["year"] == ano)
        ].copy()
        
        # Garante que 'index' é datetime para plotagem
        dff['index'] = pd.to_datetime(dff['index'])
        
        fig = go.Figure()
        
        # Adiciona trace de umidade
        fig.add_trace(go.Scatter(
            x=dff["index"],
            y=dff["HumidadeMed"],
            mode='lines+markers',
            name="Umidade Média",
            line=dict(color="rgb(0, 128, 255)"),
            marker=dict(size=4)
        ))
        
        # Mapeamento de intensidade para cor (transparência ou tonalidade de laranja)
        def get_hw_color_intensity(intensity):
            intensity_map = {
                "low-intensity": 0.4,  # Mais transparente
                "severe": 0.6,       # Médio
                "extreme": 0.8       # Menos transparente/Mais opaco
            }
            return intensity_map.get(str(intensity).strip().lower(), 0.3) # Default para opacidade baixa
        
        # Adiciona formas para dias de onda de calor
        shapes = []
        for index, row in dff.iterrows():
            is_hw_day = False
            if 'isHW' in row and pd.notna(row['isHW']):
                is_hw_day = str(row['isHW']).strip().upper() in ['VERDADEIRO', 'TRUE', '1']
            
            if is_hw_day:
                opacity = get_hw_color_intensity(row.get('HW_Intensity', 'low-intensity'))
                shapes.append({
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': row['index'] - pd.Timedelta(days=0.5),
                    'x1': row['index'] + pd.Timedelta(days=0.5),
                    'y0': 0,
                    'y1': 1,
                    'fillcolor': 'orange',
                    'opacity': opacity,
                    'line': dict(width=0),
                    'layer': 'below'
                })
        
        # Adiciona anotações para dias de onda de calor
        hw_day_annotations = []
        for index, row in dff.iterrows():
            is_hw_day = False
            if 'isHW' in row and pd.notna(row['isHW']):
                is_hw_day = str(row['isHW']).strip().upper() in ['VERDADEIRO', 'TRUE', '1']

            if is_hw_day and 'HWDay_Intensity' in row and pd.notna(row['HWDay_Intensity']):
                hw_day_annotations.append({
                    'x': row['index'],
                    'y': 1.02,
                    'xref': 'x',
                    'yref': 'paper',
                    'text': str(row['HWDay_Intensity']),
                    'showarrow': False,
                    'bgcolor': 'rgba(255, 165, 0, 0.6)',
                    'bordercolor': 'orange',
                    'borderwidth': 1,
                    'borderpad': 2,
                    'font': dict(color='white', size=9),
                    'textangle': 0,
                    'xanchor': 'center',
                    'yanchor': 'bottom'
                })

        fig.update_layout(
            title=f"Umidade Diária e Ondas de Calor em {cidade} - {ano}",
            xaxis_title="Data",
            yaxis_title="Umidade Relativa (%)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=12),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            shapes=shapes,
            annotations=hw_day_annotations
        )
        
        return fig 