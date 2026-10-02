import streamlit as st
import pandas as pd
import time
import urllib.request
import io
from streamlit_folium import st_folium
import folium

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Monitoreo Satelital Real")

# Título y botón de actualización manual alineados de forma nativa
col_titulo, col_boton = st.columns([4, 1])
with col_titulo:
    st.title("🛰️ Monitoreo Satelital Pro (Google HD)")
with col_boton:
    st.write("")
    if st.button("🔄 Actualizar Datos", width='stretch'):
        st.cache_data.clear()
        st.rerun()

# TU ENLACE REAL DE GOOGLE SHEETS
URL_DE_TU_SHEET = "https://google.com"

@st.cache_data(ttl=2)
def cargar_datos():
    url_fresca = f"{URL_DE_TU_SHEET}&cache_bypass={int(time.time())}"
    req = urllib.request.Request(url_fresca, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read()
    df = pd.read_csv(io.BytesIO(html))
    
    # Limpieza estricta de coordenadas convirtiendo comas en puntos decimales
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

    # 3. RENDERIZADO DEL MAPA SATELITAL CON FOLIUM
    if not df_f.empty:
        # Calcular centro dinámico automático enfocado en Guatemala o cualquier región
        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        # Creamos el mapa base de Folium (Sin requerir tokens de Mapbox)
        m = folium.Map(
            location=[lat_centro, lon_centro], 
            zoom_start=15, 
            control_scale=True
        )

        # INYECTAMOS EL SATÉLITE HÍBRIDO DE GOOGLE MAPS (Imágenes de alta definición + Calles)
        folium.TileLayer(
            tiles="https://google.com{x}&y={y}&z={z}",
            attr="Google Satellite Hybrid",
            name="Google Satélite",
            overlay=False,
            control=True,
            max_zoom=22 # Permite un zoom extremo a nivel de patio/techo de casa sin perder la imagen
        ).add_to(m)

        # Dibujamos cada coordenada como un marcador celeste interactivo
        for _, fila in df_f.iterrows():
            texto_popup = f"""
            <b>Usuario:</b> {fila['ENC_USER']}<br>
            <b>Fecha:</b> {fila['FECHAOC']}<br>
            <b>Segmento:</b> {fila['SEG']}<br>
            <b>Sujeto:</b> {fila['SbjNum']}
            """
            
            folium.CircleMarker(
                location=[fila['LAT_INIOC'], fila['LON_INIOC']],
                radius=8,
                popup=folium.Popup(texto_popup, max_width=300),
                color="#00FFFF",      # Borde celeste brillante
                fill=True,
                fill_color="#00FFFF",# Relleno celeste brillante
                fill_opacity=0.7
            ).add_to(m)

        # Desplegar el mapa en Streamlit de forma nativa estirado al ancho total
        st_folium(m, width=1400, height=600, returned_objects=[])

        # Tabla inferior de registros
        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, width='stretch')
    else:
        st.warning("⚠️ No se encontraron coordenadas válidas para la combinación de filtros seleccionada.")

except Exception as e:
    st.error(f"🚨 Error crítico en el procesamiento: {e}")
