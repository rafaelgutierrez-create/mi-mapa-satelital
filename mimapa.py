import streamlit as st
from streamlit_folium import st_folium
import folium

# 1. Crear el mapa base (Con un fondo neutral inicial)
m = folium.Map(location=[40.4167, -3.7037], zoom_start=18, tiles=None) # Zoom 18 para ver las casas de cerca

# 2. INYECTAR EL SATÉLITE REAL (Fotografía aérea de alta resolución)
folium.TileLayer(
    tiles='https://arcgisonline.com{z}/{y}/{x}',
    attr='Esri Satellite',
    name='Satélite Real',
    overlay=False,
    max_zoom=20 # Te permite acercarte al máximo sin que se borre
).add_to(m)

# 3. Crear el grupo para que tus puntos pinten POR ENCIMA de las casas
grupo_puntos = folium.FeatureGroup(name="Mis Datos")

# Tus coordenadas de ejemplo (Cámbialas por tus datos reales)
coordenadas = [
    [40.4167, -3.7037],
    [40.4190, -3.7050],
    [40.4120, -3.7010]
]

for coord in coordenadas:
    folium.Marker(
        location=coord, 
        popup="Detalles del Punto",
        icon=folium.Icon(color="red", icon="cloud") # Marcador visible
    ).add_to(grupo_puntos)

# 4. Acoplar los puntos encima del satélite
grupo_puntos.add_to(m)

# Renderizar en tu aplicación de Streamlit Cloud
st_folium(m, width=800, height=500)
