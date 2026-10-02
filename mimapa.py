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

# 3. Inicializar el mapa usando el renderizador oficial integrado de Mapbox
m = folium.Map(
    location=[centro_lat, centro_lon], 
    zoom_start=14,
    tiles="Mapbox Satellite Streets", # <--- Usa la configuración nativa de Folium
    API_key=MAPBOX_TOKEN,              # <--- Pasa el token de forma oficial
    max_zoom=22
)

# 4. Agregar los marcadores encima
grupo_puntos = folium.FeatureGroup(name="Mis Coordenadas")

for idx, row in data.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']], 
        popup=f"Punto #{idx+1}",
        icon=folium.Icon(color="red", icon="cloud")
    ).add_to(grupo_puntos)

grupo_puntos.add_to(m)

# 5. Desplegar en la app de Streamlit
st_folium(m, width=800, height=500, use_container_width=True)
