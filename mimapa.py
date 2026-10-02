import streamlit as st
from streamlit_folium import st_folium
import folium

# Crear el mapa base centrado
m = folium.Map(location=[14.62833, -90.49968833], zoom_start=13)

# Añadir la capa de satélite de ESRI (Esta no es bloqueada por la CSP de Streamlit)
folium.TileLayer(
    tiles='https://arcgisonline.com{z}/{y}/{x}',
    attr='Esri',
    name='Esri Satellite',
    overlay=False,
    control=True
).add_to(m)

# Añadir tus puntos de ejemplo
folium.Marker([40.4167, -3.7037], popup="Punto A").add_to(m)

# Renderizar en Streamlit
st_folium(m, width=700, height=500)
