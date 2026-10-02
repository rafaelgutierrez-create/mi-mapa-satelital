import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import urllib.request
import io

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Monitoreo Satelital Real")

# Título y botón alineados para Streamlit v2026+
col_titulo, col_boton = st.columns([4, 1])
with col_titulo:
    st.title("🛰️ Monitoreo Satelital de Alta Definición")
with col_boton:
    st.write("")
    if st.button("🔄 Actualizar Datos", width='stretch'):
        st.cache_data.clear()
        st.rerun()

URL_DE_TU_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSXnTLmB6L7QK4Tj33d016VUUD419vBnbgdQYrOHHQzJc_74VDSqDWdh3bQSrSF8oKKHjEZ5bl6PxAK/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=2)
def cargar_datos():
    url_fresca = f"{URL_DE_TU_SHEET}&cache_bypass={int(time.time())}"
    req = urllib.request.Request(url_fresca, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read()
    df = pd.read_csv(io.BytesIO(html))
    df['LAT_INIOC'] = pd.to_numeric(df['LAT_INIOC'].astype(str).str.replace(',', '.'), errors='coerce')
    df['LON_INIOC'] = pd.to_numeric(df['LON_INIOC'].astype(str).str.replace(',', '.'), errors='coerce')
    return df.dropna(subset=['LAT_INIOC', 'LON_INIOC'])

try:
    df = cargar_datos()
    df_f = df.copy()

    # 2. Panel de filtros interactivos en columnas
    st.subheader("🎛️ Panel de Filtros")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        usuarios = ["Todos"] + sorted(list(df['ENC_USER'].dropna().unique()))
        user_sel = st.selectbox("Usuario:", usuarios)
    if user_sel != "Todos":
        df_f = df_f[df_f['ENC_USER'] == user_sel]

    with col2:
        fechas = ["Todas"] + sorted(list(df_f['FECHAOC'].dropna().astype(str).unique()))
        fecha_sel = st.selectbox("Fecha:", fechas)
    if fecha_sel != "Todas":
        df_f = df_f[df_f['FECHAOC'].astype(str) == fecha_sel]

    with col3:
        df_f['SEG'] = pd.to_numeric(df_f['SEG'], errors='coerce').fillna(0).astype(int)
        segmentos = ["Todos"] + sorted(list(df_f['SEG'].unique()))
        seg_sel = st.selectbox("Segmento:", segmentos)
    if seg_sel != "Todos":
        df_f = df_f[df_f['SEG'] == int(seg_sel)]

    with col4:
        df_f['SbjNum'] = pd.to_numeric(df_f['SbjNum'], errors='coerce').fillna(0).astype(int)
        sujetos = ["Todos"] + sorted(list(df_f['SbjNum'].unique()))
        sbj_sel = st.selectbox("Sujeto:", sujetos)
    if sbj_sel != "Todos":
        df_f = df_f[df_f['SbjNum'] == int(sbj_sel)]

    st.markdown("---")

    if not df_f.empty:
        # Calcular el centro geográfico automático para enfocar Guatemala o cualquier país
        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        # Configuración de la cámara del visor
        view_state = pdk.ViewState(
            latitude=lat_centro,
            longitude=lon_centro,
            zoom=16,
            pitch=0
        )

        # Capa de los puntos celestes interactivos (Formato corregido)
        capa_puntos = pdk.Layer(
            "ScatterplotLayer",
            df_f,
            get_position="[LON_INIOC, LAT_INIOC]",
            get_color="[0, 255, 255, 200]",  # RGBA: Celeste brillante con opacidad
            get_radius=12,                  # Radio de los puntos fijado en metros reales
            pickable=True,
        )

        # Capa satelital híbrida de Google (Muestra casas, calles y vegetación en HD)
        capa_satelite = pdk.Layer(
            "TileLayer",
            "https://google.com{x}&y={y}&z={z}",
            tile_size=256
        )

        # Renderizado del mapa unificado en Streamlit
        st.pydeck_chart(pdk.Deck(
            map_style=None, # Desactivamos el mapa base para que no interfiera con el satélite
            initial_view_state=view_state,
            layers=[capa_satelite, capa_puntos],
            tooltip={"text": "Usuario: {ENC_USER}\nSegmento: {SEG}\nFecha: {FECHAOC}"}
        ))

        # Tabla de datos
        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, width='stretch')
    else:
        st.warning("⚠️ No se encontraron coordenadas para la combinación de filtros seleccionada.")

except Exception as e:
    st.error(f"🚨 Error de procesamiento: {e}")
