import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd

# 1. Coloca tu token aquí (Debe empezar con pk.xxx)
MAPBOX_TOKEN = "TU_TOKEN_DE_MAPBOX_AQUI"

# 2. Coordenadas de ejemplo de Guatemala
data = pd.DataFrame({
    'lat': [14.62833, 14.61833667, 14.65187],
    'lon': [-90.49968833, -90.50662, -90.47395167]
})

centro_lat = data['lat'].mean()
centro_lon = data['lon'].mean()

# 3. Crear mapa base sin fondo genérico
m = folium.Map(
    location=[centro_lat, centro_lon], 
    zoom_start=14,
    tiles=None
)

# 4. URL Corregida de Mapbox (Sintaxis exacta para evitar el fondo gris)
mapbox_url = (
    "https://mapbox.com"
    "{z}/{x}/{y}?access_token=" + MAPBOX_TOKEN
)

folium.TileLayer(
    tiles=mapbox_url,
    attr='Mapbox Satellite',
    name='Satélite Mapbox',
    overlay=False,
    tileSize=512,           # <--- CRÍTICO: Mapbox usa por defecto 512px en v1
    zoomOffset=-1,          # <--- CRÍTICO: Ajusta la escala para que no se desfase
    max_zoom=22,
    max_native_zoom=19
).add_to(m)

# 5. Agregar los marcadores encima
grupo_puntos = folium.FeatureGroup(name="Mis Coordenadas")

for idx, row in data.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']], 
        popup=f"Punto #{idx+1}",
        icon=folium.Icon(color="red", icon="cloud")
    ).add_to(grupo_puntos)

grupo_puntos.add_to(m)

# 6. Desplegar en la app
st_folium(m, width=800, height=500, use_container_width=True)
