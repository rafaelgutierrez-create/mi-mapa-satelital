import streamlit as st
from streamlit_folium import st_folium
import folium

# 1. Crear el mapa base especificando el zoom inicial de cerca (17 o 18)
m = folium.Map(
    location=[40.4167, -3.7037],  # <--- Reemplaza por tus coordenadas reales
    zoom_start=18,
)

# 2. Inyectar la capa satelital directa (Formato plano compatible al 100%)
folium.TileLayer(
    tiles='https://google.com{x}&y={y}&z={z}', # lyrs=y incluye las casas y nombres de calles
    attr='Google',
    name='Google Satellite',
    overlay=True, # Obliga a superponerlo sobre el fondo base para evitar la pantalla transparente
    max_zoom=20,
).add_to(m)

# 3. Crear el grupo de tus datos
grupo_puntos = folium.FeatureGroup(name="Mis Ubicaciones")

# Tus coordenadas reales (Ejemplo de prueba)
coordenadas = [
    [40.4167, -3.7037],
    [40.4190, -3.7050],
    [40.4120, -3.7010]
]

for coord in coordenadas:
    folium.Marker(
        location=coord, 
        popup="Información del punto",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(grupo_puntos)

# 4. Unir todo al mapa base
grupo_puntos.add_to(m)

# Renderizar en tu app de Streamlit Cloud
st_folium(m, width=800, height=500, use_container_width=True)
