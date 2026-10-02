import streamlit as st
import pandas as pd
import requests
import io
from streamlit_folium import st_folium
import folium

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Rastreo Satelital Pro")

st.title("🛰️ Monitoreo Satelital de Alta Definición (Google Maps)")

# Enlace real de tu Google Sheet fijo
URL_DE_TU_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSXnTLmB6L7QK4Tj33d016VUUD419vBnbgdQYrOHHQzJc_74VDSqDWdh3bQSrSF8oKKHjEZ5bl6PxAK/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=2)
def cargar_datos():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL_DE_TU_SHEET, headers=headers, timeout=15)
    df = pd.read_csv(io.StringIO(response.text))
    
    # Limpieza estricta de coordenadas
    df['LAT_INIOC'] = pd.to_numeric(df['LAT_INIOC'].astype(str).str.replace(',', '.'), errors='coerce')
    df['LON_INIOC'] = pd.to_numeric(df['LON_INIOC'].astype(str).str.replace(',', '.'), errors='coerce')
    return df.dropna(subset=['LAT_INIOC', 'LON_INIOC'])

try:
    df = cargar_datos()

    if not df.empty:
        # Centro automático en Ciudad de Guatemala
        lat_centro = df['LAT_INIOC'].mean()
        lon_centro = df['LON_INIOC'].mean()

        # Creamos el mapa base CONFIGURADO CORRECTAMENTE sin mapa base por defecto (tiles=None)
        m = folium.Map(
            location=[lat_centro, lon_centro], 
            zoom_start=16, 
            tiles=None  # <--- ESTO OBLIGA A QUE NO SE META EL MAPA DE CALLES GRIS
        )

        # CAPA CORRECTA: Satélite de Google Maps en Máxima Resolución (Híbrido: Satélite + Calles)
        folium.TileLayer(
            tiles="https://google.com{x}&y={y}&z={z}",
            attr="Google",
            name="Google Satélite",
            max_zoom=22, # <--- Zoom ultra profundo sin que se borre
            overlay=False,
            control=False
        ).add_to(m)

        # Dibujar tus puntos celestes interactivos
        for _, fila in df.iterrows():
            texto_popup = f"<b>Usuario:</b> {fila.get('ENC_USER', 'N/A')}<br><b>Segmento:</b> {fila.get('SEG', 'N/A')}"
            
            folium.CircleMarker(
                location=[fila['LAT_INIOC'], fila['LON_INIOC']],
                radius=8,
                popup=folium.Popup(texto_popup, max_width=250),
                color="#00FFFF",
                fill=True,
                fill_color="#00FFFF",
                fill_opacity=0.8
            ).add_to(m)

        # Desplegar el mapa en Streamlit
        st_folium(m, width=1400, height=600, returned_objects=[])
        
        # Tabla abajo
        st.dataframe(df, width='stretch')

except Exception as e:
    st.error(f"🚨 Error: {e}")
