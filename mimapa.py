import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd

# 1. Cargamos tus coordenadas exactas de Guatemala
data = pd.DataFrame({
    'lat': [14.62833, 14.61833667, 14.65187],
    'lon': [-90.49968833, -90.50662, -90.47395167]
})

# Calculamos el centro geográfico exacto de tus puntos
centro_lat = data['lat'].mean()
centro_lon = data['lon'].mean()

# 2. Inicializar el mapa base configurando las restricciones de Zoom de una vez
m = folium.Map(
    location=[centro_lat, centro_lon], 
    zoom_start=14,
    tiles=None # Apaga el mapa beige por completo de entrada
)

# 3. Inyectar el servidor Satelital de ESRI (Aprobado al 100% por la seguridad de Streamlit)
folium.TileLayer(
    tiles='https://arcgisonline.com{z}/{y}/{x}',
    attr='Esri Satellite',
    name='Satélite Real',
    overlay=False,       # Obliga a que sea el fondo principal, eliminando cualquier capa vacía
    max_zoom=20,         # Zoom máximo permitido en la interfaz
    max_native_zoom=17   # TRUCO: Cuando pases el zoom 17 en Centroamérica, estira la foto en lugar de borrarse
).add_to(m)

# 4. Dibujar los puntos sobre el mapa satelital
grupo_puntos = folium.FeatureGroup(name="Mis Coordenadas")

for idx, row in data.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']], 
        popup=f"Punto #{idx+1} ({row['lat']}, {row['lon']})",
        icon=folium.Icon(color="red", icon="cloud")
    ).add_to(grupo_puntos)

grupo_puntos.add_to(m)

# 5. Desplegar en tu servidor web
st_folium(m, width=800, height=500, use_container_width=True)
