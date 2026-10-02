import streamlit as st
from streamlit_folium import st_folium
import folium

# 1. Crear mapa base centrado
m = folium.Map(location=[40.4167, -3.7037], zoom_start=13)

# 2. Inyectar capa satelital libre de Esri
folium.TileLayer(
    tiles='https://arcgisonline.com{z}/{y}/{x}',
    attr='Esri Satellite',
    name='Satélite',
    overlay=False
).add_to(m)

# 3. CRÍTICO: Crear un grupo para tus elementos/puntos
grupo_puntos = folium.FeatureGroup(name="Mis Puntos")

# Coordenadas de ejemplo para el bucle
coordenadas = [
    [40.4167, -3.7037],
    [40.4190, -3.7050],
    [40.4120, -3.7010]
]

# Añadir los marcadores AL GRUPO, no directamente al mapa base
for coord in coordenadas:
    folium.Marker(
        location=coord, 
        popup="Información del punto",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(grupo_puntos)

# 4. Añadir el grupo completo al mapa final
grupo_puntos.add_to(m)

# Renderizar en tu app de Streamlit
st_folium(m, width=700, height=500)
