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

     # 3. GENERACIÓN DEL MAPA CON GOOGLE SATÉLITE HYBRID (ZOOM ILIMITADO)
    if not df_f.empty:
        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        # Crear mapa base de Folium centrado
        m = folium.Map(location=[lat_centro, lon_centro], zoom_start=16, control_scale=True)

        # AGREGAMOS EL SATÉLITE REAL DE GOOGLE CON ZOOM MÁXIMO DE 20
        folium.TileLayer(
            tiles="http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}",
            attr="Google Maps Satellite",
            name="Google Satélite",
            max_zoom=20,
            overlay=False,
            control=False
        ).add_to(m)

        # Dibujar tus puntos amarillos con ventanas flotantes de información
        for _, fila in df_f.iterrows():
            texto_popup = f"""
            <b>Usuario:</b> {fila['ENC_USER']}<br>
            <b>Fecha:</b> {fila['FECHAOC']}<br>
            <b>Segmento:</b> {fila['SEG']}<br>
            <b>Sujeto:</b> {fila['SbjNum']}
            """
            folium.CircleMarker(
                location=[fila['LAT_INIOC'], fila['LON_INIOC']],
                radius=7,
                popup=folium.Popup(texto_popup, max_width=250),
                color="#FFFF00",       # CAMBIADO: Borde amarillo intenso
                fill=True,
                fill_color="#FFFF00",  # CAMBIADO: Relleno amarillo intenso
                fill_opacity=0.9       # Subido ligeramente a 0.9 para que brille más
            ).add_to(m)

        # Renderizar en Streamlit al ancho de la pantalla
        st_folium(m, width=1400, height=600, returned_objects=[])


        # Tabla inferior de registros
        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, width='stretch')
    else:
        st.warning("⚠️ No se encontraron coordenadas válidas para los filtros seleccionados.")

except Exception as e:
    st.error(f"🚨 Error crítico en el procesamiento: {e}")
