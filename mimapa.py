import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Monitoreo Satelital Real HD")

# Ajuste de columnas superiores para el título y botón (Línea 11 fija)
col_titulo, col_boton = st.columns(2)
with col_titulo:
    st.title("🛰️ Monitoreo Satelital de Alta Definición (Google Tiles)")
with col_boton:
    st.write("")
    st.write("")
    if st.button("🔄 Actualizar Datos", width='stretch'):
        st.cache_data.clear()
        st.rerun()

# Extracción y limpieza de tu token de Mapbox desde tu config.toml anterior
try:
    raw_key = st.secrets["GOOGLE_MAPS_API_KEY"] # Mantenemos el nombre de tu secreto actual
    MAPBOX_TOKEN = str(raw_key).replace('\n', '').replace('\r', '').strip().replace('"', '').replace("'", "")
except Exception:
    MAPBOX_TOKEN = ""

# TU ENLACE REAL DE GOOGLE SHEETS
URL_DE_TU_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSXnTLmB6L7QK4Tj33d016VUUD419vBnbgdQYrOHHQzJc_74VDSqDWdh3bQSrSF8oKKHjEZ5bl6PxAK/pub?gid=0&single=true&output=csv"


@st.cache_data(ttl=2)
def cargar_datos():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(URL_DE_TU_SHEET, headers=headers, timeout=15)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    
    # Limpieza de coordenadas convirtiendo comas en puntos decimales
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

    # 3. GENERACIÓN DEL MAPA INYECTANDO LAS TESELAS DE GOOGLE QUE ENCONTRASTE
    if not df_f.empty:
        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        # Usamos px.scatter_map (Sintaxis nativa actual 2026 de Plotly)
        fig = px.scatter_map(
            df_f, 
            lat="LAT_INIOC", 
            lon="LON_INIOC",
            hover_name="ENC_USER", 
            hover_data={"SbjNum": True, "FECHAOC": True, "SEG": True},
            zoom=16,  # Un zoom de 16 para arrancar viendo los techos de las casas de inmediato
            height=650
        )
        
        # AQUÍ ESTÁ EL TRUCO MAGNÍFICO: Inyectamos tu link de Google como la capa ráster base
        fig.update_layout(
            map={
                "style": "white-bg", # Quitamos las calles grises molestas de Mapbox
                "center": {"lat": lat_centro, "lon": lon_centro},
                "layers": [{
                    "sourcetype": "raster",
                    # Usamos la URL exacta que encontraste en el foro (cambiando http por https para que Streamlit Cloud lo acepte)
                    "source": ["https://google.com{x}&y={y}&z={z}"],
                    "below": "traces" # Esto obliga a que los puntos celestes queden POR ENCIMA del satélite
                }]
            },
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        
        # Marcadores celestes (Cyan) de alta visibilidad para que contrasten sobre el satélite oscuro
        fig.update_traces(
            marker=dict(size=14, color="cyan", opacity=0.9)
        )
        
        # Renderizado en Streamlit
        st.plotly_chart(fig, width='stretch')
        
        # Tabla inferior de registros
        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, width='stretch')
    else:
        st.warning("⚠️ No se encontraron coordenadas válidas para la combinación de filtros seleccionada.")

except Exception as e:
    st.error(f"🚨 Error crítico en el procesamiento: {e}")
