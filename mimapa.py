import streamlit as st
import pandas as pd
import plotly.express as px
import time
import urllib.request
import io

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Monitoreo Satelital Real")

# Título y botón de actualización manual alineados de forma nativa
col_titulo, col_boton = st.columns([4, 1])
with col_titulo:
    st.title("🛰️ Monitoreo Satelital de Alta Definición")
with col_boton:
    st.write("")
    if st.button("🔄 Actualizar Datos", width='stretch'):
        st.cache_data.clear()
        st.rerun()

# ENLACE REAL DE TU SHEET (Formato CSV)
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
    
    # Saneamiento de columnas para evitar fallos en los selectores por tipos mixtos
    if 'SEG' in df.columns:
        df['SEG'] = pd.to_numeric(df['SEG'], errors='coerce').fillna(0).astype(int)
    if 'SbjNum' in df.columns:
        df['SbjNum'] = pd.to_numeric(df['SbjNum'], errors='coerce').fillna(0).astype(int)
        
    return df.dropna(subset=['LAT_INIOC', 'LON_INIOC'])

try:
    df = cargar_datos()
    df_f = df.copy()

    # 2. PANEL DE FILTROS EN COLUMNAS (Alineación idéntica a tu diseño original)
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

    # 3. GENERACIÓN DEL MAPA SATELITAL INTEGRADO (MÁXIMA ESTABILIDAD EN LA NUBE)
    if not df_f.empty:
        # Usamos px.scatter_map (Sintaxis oficial nativa para Plotly moderna en 2026)
        fig = px.scatter_map(
            df_f, 
            lat="LAT_INIOC", 
            lon="LON_INIOC",
            hover_name="ENC_USER", 
            hover_data={"SbjNum": True, "FECHAOC": True, "SEG": True},
            zoom=14,  # Zoom óptimo para el área urbana de Ciudad de Guatemala
            height=650
        )
        
        # PROYECCIÓN SATELITAL NATIVA SIN CAPAS EXTERNAS QUE CAUSEN BLOQUEOS CORS
        fig.update_layout(
            map_style="satellite-streets", # Estilo nativo que invoca las fotos HD de Mapbox de forma directa
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        
        # Estilo estético y llamativo para los puntos de geolocalización
        fig.update_traces(
            marker=dict(size=14, color="cyan", opacity=0.9)
        )
        
        # Mostrar el mapa en pantalla estirado horizontalmente (Sintaxis Streamlit 2026+)
        st.plotly_chart(fig, width='stretch')
        
        # Tabla inferior de registros
        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, width='stretch')
    else:
        st.warning("⚠️ No se encontraron coordenadas válidas para la combinación de filtros seleccionada.")

except Exception as e:
    st.error(f"🚨 Error crítico en el procesamiento: {e}")
