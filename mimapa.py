import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd

# 1. Tus coordenadas de Centroamérica (Guatemala)
data = pd.DataFrame({
    'lat': [14.62833, 14.61833667, 14.65187],
    'lon': [-90.49968833, -90.50662, -90.47395167]
})

# Calcular el centro automático
centro_lat = data['lat'].mean()
centro_lon = data['lon'].mean()

# 2. Inicializar el mapa APAGANDO el fondo por defecto (tiles=None)
m = folium.Map(
    location=[centro_lat, centro_lon], 
    zoom_start=14,
    tiles=None  # <--- CRÍTICO: Esto elimina el mapa beige que ves en tu imagen
)

# 3. Forzar el satélite híbrido de Google como la capa base única
folium.TileLayer(
    tiles='https://google.com{x}&y={y}&z={z}', # lyrs=y para Satélite + Calles
    attr='Google',
    name='Google Hybrid',
    overlay=False,            # <--- Al ser False, se convierte en el mapa principal obligado
    max_zoom=22,              
    max_native_zoom=18,       # Protege el zoom en Centroamérica para que no desaparezca
).add_to(m)

# 4. Dibujar tus puntos encima de la foto satelital
grupo_puntos = folium.FeatureGroup(name="Mis Coordenadas")

for idx, row in data.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']], 
        popup=f"Punto #{idx+1}",
        icon=folium.Icon(color="red", icon="cloud")
    ).add_to(grupo_puntos)

grupo_puntos.add_to(m)

# 5. Renderizar en Streamlit Cloud
st_folium(m, width=800, height=500, use_container_width=True)
