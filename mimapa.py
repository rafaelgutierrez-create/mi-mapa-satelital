import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd

# 1. Definimos tus coordenadas de ejemplo para Centroamérica (Guatemala)
data = pd.DataFrame({
    'lat': [14.62833, 14.61833667, 14.65187],
    'lon': [-90.49968833, -90.50662, -90.47395167]
})

# Calcular el centro exacto de tus puntos para que el mapa abra justo ahí
centro_lat = data['lat'].mean()
centro_lon = data['lon'].mean()

# 2. Inicializar el mapa base vacío centrado en tu zona de interés
m = folium.Map(
    location=[centro_lat, centro_lon], 
    zoom_start=14, # Zoom inicial ideal para ver el grupo completo de puntos
)

# 3. Inyectar capa satelital híbrida (FOTOS REALES + CALLES) resolviendo el problema del zoom
folium.TileLayer(
    tiles='https://google.com{x}&y={y}&z={z}', # lyrs=y es el híbrido perfecto de Google
    attr='Google',
    name='Google Hybrid',
    overlay=True,             # Obliga a pintar encima de cualquier fondo gris
    max_zoom=22,              # <--- Zoom máximo permitido al usuario al interactuar
    max_native_zoom=18,       # <--- TRUCO CRÍTICO: Evita que el mapa se borre en Centroamérica
).add_to(m)

# 4. Agrupar y dibujar los puntos sobre el terreno real de las viviendas
grupo_puntos = folium.FeatureGroup(name="Mis Coordenadas")

# Recorrer tu DataFrame para pintar cada marcador
for idx, row in data.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']], 
        popup=f"Punto #{idx+1} ({row['lat']}, {row['lon']})",
        icon=folium.Icon(color="red", icon="cloud")
    ).add_to(grupo_puntos)

# Unir las capas vectoriales encima del satélite
grupo_puntos.add_to(m)

# 5. Renderizar de forma responsiva en Streamlit Cloud
st_folium(m, width=800, height=500, use_container_width=True)
