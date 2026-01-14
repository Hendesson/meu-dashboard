# Pacotes necessários
import geopandas as gpd
import folium
from branca.element import Figure

# --- 1. Ler shapefiles
BR_UF = gpd.read_file(r'D:\pibic_dash\BR_UF_2024.shp')
RM = gpd.read_file(r'D:\pibic_dash\pibic_dash\rms_geo.shp')

# --- 2. Criar o mapa base
# Centro aproximado do Brasil
m = folium.Map(
    location=[-15.77972, -47.92972],
    zoom_start=4,
    tiles=None,  # Não adiciona nenhum tile base automaticamente
    control_scale=True
)

# Adiciona o tile CartoDB positron, mas sem adicionar ao controle de camadas
folium.TileLayer(
    'CartoDB positron',
    name='CartoDB positron',
    control=False  # Não aparece na legenda
).add_to(m)

# --- 3. Adicionar polígonos das UFs
folium.GeoJson(
    BR_UF,
    name='Unidades Federativas',
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': '#666666',
        'weight': 2,
        'fillOpacity': 0.1
    }
).add_to(m)

# --- 4. Adicionar Regiões Metropolitanas com popup
def style_function(feature):
    return {
        'fillColor': '#FF4500',
        'color': '#FF4500',
        'weight': 3,
        'fillOpacity': 0.1
    }

def highlight_function(feature):
    return {
        'fillColor': '#FF4500',
        'color': '#FF4500',
        'weight': 4,
        'fillOpacity': 0.5
    }

# Criar popups para cada região metropolitana
for idx, row in RM.iterrows():
    # Criar o conteúdo do popup com as colunas solicitadas
    popup_content = f"""
    <div style='font-family: Arial, sans-serif; padding: 10px;'>
        <h4 style='color: #FF4500; margin-bottom: 15px;'>{row['NOME_CATME']}</h4>
        <table style='width:100%; border-collapse: collapse;'>
            <tr style='background-color: #f8f9fa;'>
                <th style='padding: 8px; text-align: left; border-bottom: 1px solid #ddd;'>Variável</th>
                <th style='padding: 8px; text-align: right; border-bottom: 1px solid #ddd;'>Valor</th>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #ddd;'>Temperatura Máxima (T95)</td>
                <td style='padding: 8px; text-align: right; border-bottom: 1px solid #ddd;'>{row['T95_TMAX']:.1f}°C</td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #ddd;'>Temperatura Média</td>
                <td style='padding: 8px; text-align: right; border-bottom: 1px solid #ddd;'>{row['medias_HW_']:.1f}°C</td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #ddd;'>Valor EHF</td>
                <td style='padding: 8px; text-align: right; border-bottom: 1px solid #ddd;'>{row['medias_H_1']:.1f}</td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #ddd;'>Anomalia de Temperatura</td>
                <td style='padding: 8px; text-align: right; border-bottom: 1px solid #ddd;'>{row['medias_H_2']:.1f}°C</td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #ddd;'>Amplitude Térmica</td>
                <td style='padding: 8px; text-align: right; border-bottom: 1px solid #ddd;'>{row['medias_H_3']:.1f}°C</td>
            </tr>
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #ddd;'>Duração</td>
                <td style='padding: 8px; text-align: right; border-bottom: 1px solid #ddd;'>{row['medias_H_4']:.1f} dias</td>
            </tr>
        </table>
    </div>
    """
    
    # Criar o GeoJson para esta região
    folium.GeoJson(
        row.geometry,
        name=row['NOME_CATME'],
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=row['NOME_CPTL'],
        popup=folium.Popup(popup_content, max_width=400)
    ).add_to(m)

# --- 5. Adicionar controles
folium.LayerControl(collapsed=False).add_to(m)

# --- 6. Adicionar título ao mapa
title_html = '''
    <h3 style="position:absolute;z-index:100000;left:50px;top:10px;background-color:white;padding:10px;border-radius:5px;box-shadow:0 0 5px rgba(0,0,0,0.2);">
        Mapa de Regiões Metropolitanas
    </h3>
'''
m.get_root().html.add_child(folium.Element(title_html))

# --- 7. Salvar mapa
m.save('mapa_interativo.html')