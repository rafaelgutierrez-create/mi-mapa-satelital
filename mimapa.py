import streamlit as st
import pandas as pd
import requests
import io
from streamlit_folium import st_folium
import folium

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Monitoreo Satelital Ultra HD")

# Título y botón de actualización manual
col_titulo, col_boton = st.columns([4, 1])
with col_titulo:
    st.title("🛰️ Monitoreo Satelital de Alta Definición (Google Maps)")
with col_boton:
    st.write("")
    st.write("")
    if st.button("🔄 Actualizar Datos", width='stretch'):
        st.cache_data.clear()
        st.rerun()

# TU ENLACE REAL DE GOOGLE SHEETS
URL_DE_TU_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSXnTLmB6L7QK4Tj33d016VUUD419vBnbgdQYrOHHQzJc_74VDSqDWdh3bQSrSF8oKKHjEZ5bl6PxAK/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=2)
def cargar_datos():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL_DE_TU_SHEET, headers=headers, timeout=15)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    
    # Limpieza de coordenadas
    df['LAT_INIOC'] = pd.to_numeric(df['LAT_INIOC'].astype(str).str.replace(',', '.'), errors='coerce')
    df['LON_INIOC'] = pd.to_numeric(df['LON_INIOC'].astype(str).str.replace(',', '.'), errors='coerce')
    
    if 'SEG' in df.columns:
        df['SEG'] = pd.to_numeric(df['SEG'], errors='coerce').fillna(0).astype(int)
    if 'SbjNum' in df.columns:
        df['SbjNum'] = pd.to_numeric(df['SbjNum'], errors='coerce').fillna(0).astype(int)
        
    return df.dropna(subset=['LAT_INIOC', 'LON_INIOC'])

try:
    df = cargar_datos()
    df_f = df.copy()

    # 2. PANEL DE FILTROS EN COLUMNAS
    st.subheader("🎛️ Panel de Filtros")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        usuarios = ["Todos"] + sorted(list(df['ENC_USER'].dropna().unique()))
        user_sel = st.selectbox("Usuario (ENC_USER):", usuarios)
    if user_sel != "Todos":
        df_f = df_f[df_f['ENC_USER'] == user_sel]

    with col2:
        fechas = ["Todas"] + sorted(list(df_f['FECHAOC'].dropna().astype(str).unique()))
        fecha_sel = st.selectbox("Fecha (FECHAOC):", fechas)
    if fecha_sel != "Todas":
        df_f = df_f[df_f['FECHAOC'].astype(str) == fecha_sel]

    with col3:
        segmentos = ["Todos"] + sorted(list(df_f['SEG'].unique()))
        seg_sel = st.selectbox("Segmento (SEG):", segmentos)
    if seg_sel != "Todos":
        df_f = df_f[df_f['SEG'] == int(seg_sel)]

    with col4:
        sujetos = ["Todos"] + sorted(list(df_f['SbjNum'].unique()))
        sbj_sel = st.selectbox("Sujeto (SbjNum):", sujetos)
    if sbj_sel != "Todos":
        df_f = df_f[df_f['SbjNum'] == int(sbj_sel)]

    st.markdown("---")

        # 3. GENERACIÓN DEL MAPA CON PLOTLY GRAPH OBJECTS (HOVER AUTOMÁTICO + GOOGLE TILES)
    if not df_f.empty:
        import plotly.graph_objects as go

        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        # Construimos el mapa con etiquetas flotantes instantáneas al pasar el cursor
        fig = go.Figure(go.Scattermap(
            lat=df_f["LAT_INIOC"],
            lon=df_f["LON_INIOC"],
            mode='markers',
            # Marcadores de color amarillo intenso de alta visibilidad
            marker=go.scattermap.Marker(size=14, color='#FFFF00', opacity=0.9),
            # Texto personalizado idéntico al de tu imagen
            text="Usuario: " + df_f["ENC_USER"].astype(str) + "<br>Sujeto: " + df_f["SbjNum"].astype(str),
            hoverinfo='text'
        ))

        # Inyectamos tu enlace de Google Satélite de forma nativa para que no se borre al hacer zoom
        fig.update_layout(
            map={
                "style": "white-bg", # Quitamos el mapa vectorial base
                "center": {"lat": lat_centro, "lon": lon_centro},
                "zoom": 16,
                "layers": [{
                    "sourcetype": "raster",
                    "source": ["https://google.com{x}&y={y}&z={z}"],
                    "below": "traces" # Obliga a los puntos amarillos a quedar arriba del satélite
                }]
            },
            margin={"r":0,"t":0,"l":0,"b":0}
        )

        # Renderizado moderno adaptado a Streamlit
        st.plotly_chart(fig, width='stretch')

        # Tabla inferior de registros
        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, width='stretch')
    else:
        st.warning("⚠️ No se encontraron coordenadas válidas para los filtros seleccionados.")

except Exception as e:
    st.error(f"🚨 Error crítico en el procesamiento: {e}")
