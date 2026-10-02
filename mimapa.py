import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd

# 1. Copia aquí tu token real de Mapbox (Debe empezar con pk.xxx)
MAPBOX_TOKEN = "pk.eyJ1IjoicmFuZ2VsZ2MiLCJhIjoiY211cjg2MWVjMGptajJ6cHoxNXpneGcycyJ9.qj2hk63Sxn9nbKlIsocP3w"

# 2. Cargamos tus coordenadas de Guatemala
data = pd.DataFrame({
    'lat': [14.62833, 14.61833667, 14.65187],
    'lon': [-90.49968833, -90.50662, -90.47395167]
})

# Cálculo automático del centro para enfocar tus datos
centro_lat = data['lat'].mean()
centro_lon = data['lon'].mean()

# 3. Inicializar el mapa borrando el fondo beige por defecto
m = folium.Map(
    location=[centro_lat, centro_lon], 
    zoom_start=14,
    tiles=None # Elimina por completo OpenStreetMap de la base
)

# 4. Inyectar el Satélite Híbrido Oficial de Mapbox usando la API oficial
# Esto descarga directamente las imágenes satelitales detalladas y permitidas en la nube
folium.TileLayer(
    tiles=f'https://mapbox.com{{z}}/{{x}}/{{y}}?access_token={MAPBOX_TOKEN}',
    attr='Mapbox Satellite Streets',
    name='Satélite Mapbox',
    overlay=False,        # Lo fija como el piso base obligado del mapa
    max_zoom=22,          # Te permite hacer zoom profundo
    max_native_zoom=20    # Mantiene la visualización de casas estable a máxima cercanía
).add_to(m)

# 5. Crear el grupo de puntos y agregarlos sobre el mapa
grupo_puntos = folium.FeatureGroup(name="Mis Coordenadas")

for idx, row in data.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']], 
        popup=f"Punto #{idx+1} ({row['lat']}, {row['lon']})",
        icon=folium.Icon(color="red", icon="cloud")
    ).add_to(grupo_puntos)

grupo_puntos.add_to(m)

# 6. Desplegar en Streamlit Cloud
st_folium(m, width=800, height=500, use_container_width=True)
