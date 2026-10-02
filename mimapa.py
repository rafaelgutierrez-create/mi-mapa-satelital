import streamlit as st
import pandas as pd
import plotly.express as px
import time
import urllib.request
import io

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Monitoreo Satelital Real3")

# CORRECCIÓN DE COLUMNAS: Definimos las proporciones fijas para evitar el error de inicialización
col_titulo, col_boton = st.columns([4, 1])
with col_titulo:
    st.title("🛰️ Rastreo Satelital Multi-Filtro4")
with col_boton:
    st.write("") 
    st.write("") 
    if st.button("🔄 Actualizar Datos", width='stretch'):
        st.cache_data.clear()
        st.rerun()

# Enlace de Google Sheets (Formato CSV)
URL_DE_TU_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSXnTLmB6L7QK4Tj33d016VUUD419vBnbgdQYrOHHQzJc_74VDSqDWdh3bQSrSF8oKKHjEZ5bl6PxAK/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=2)
def cargar_datos():
    url_fresca = f"{URL_DE_TU_SHEET}&cache_bypass={int(time.time())}"
    req = urllib.request.Request(url_fresca, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as response:
        html = response.read()
        
    df = pd.read_csv(io.BytesIO(html))
    
    # Limpieza estricta de coordenadas convirtiendo comas en puntos
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
        usuarios_lista = sorted([str(x) for x in df['ENC_USER'].dropna().unique() if str(x).strip() != ""])
        usuarios = ["Todos"] + usuarios_lista
        user_sel = st.selectbox("Usuario (ENC_USER):", usuarios)
    if user_sel != "Todos":
        df_f = df_f[df_f['ENC_USER'].astype(str) == user_sel]

    with col2:
        fechas_lista = sorted([str(x) for x in df_f['FECHAOC'].dropna().unique() if str(x).strip() != ""])
        fechas = ["Todas"] + fechas_lista
        fecha_sel = st.selectbox("Fecha (FECHAOC):", fechas)
    if fecha_sel != "Todas":
        df_f = df_f[df_f['FECHAOC'].astype(str) == fecha_sel]

    with col3:
        segmentos_lista = sorted([int(x) for x in df_f['SEG'].dropna().unique()])
        segmentos = ["Todos"] + segmentos_lista
        seg_sel = st.selectbox("Segmento (SEG):", segmentos)
    if seg_sel != "Todos":
        df_f = df_f[df_f['SEG'] == int(seg_sel)]

    with col4:
        sujetos_lista = sorted([int(x) for x in df_f['SbjNum'].dropna().unique()])
        sujetos = ["Todos"] + sujetos_lista
        sbj_sel = st.selectbox("Sujeto (SbjNum):", sujetos)
    if sbj_sel != "Todos":
        df_f = df_f[df_f['SbjNum'] == int(sbj_sel)]

    st.markdown("---")

   # 3. GENERACIÓN DEL MAPA CON CAPA HÍBRIDA DE ZOOM ULTRA-PROFUNDO
    if not df_f.empty:
        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        fig = px.scatter_map(
            df_f, 
            lat="LAT_INIOC", 
            lon="LON_INIOC",
            hover_name="ENC_USER", 
            hover_data={"SbjNum": True, "FECHAOC": True, "SEG": True},
            zoom=15,  
            height=650
        )
        
        # CONFIGURACIÓN MAESTRA CON INFRAESTRUCTURA DE GOOGLE MAPS
        fig.update_layout(
            map={
                "style": "white-bg",  # Canvas base
                "center": {"lat": 40.4167, "lon": -3.7037},  # <--- CAMBIA ESTO por el centro de tus datos (Ej: Madrid)
                "zoom": 12,  # <--- Zoom inicial (ajústalo según tu escala)
                "layers": [
                    {
                        "sourcetype": "raster",
                        "source": ["https://google.com{x}&y={y}&z={z}"],  # URL en lista []
                        "below": "traces",
                    }
                ],
            }
        )




        
        # Estilo de puntos celestes de alta visibilidad
        fig.update_traces(marker=dict(size=14, color="cyan", opacity=0.9))
        
        st.plotly_chart(fig, width='stretch')
        
        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, width='stretch')
    else:
        st.warning("⚠️ No se encontraron coordenadas válidas para la combinación de filtros seleccionada.")

except Exception as e:
    st.error(f"🚨 Error crítico en el procesamiento: {e}")
