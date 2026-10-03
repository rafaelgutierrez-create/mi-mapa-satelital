import streamlit as st
import pandas as pd
import requests
import io

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Monitoreo Satelital Real HD")

# Ajuste estricto de columnas superiores
col_titulo, col_boton = st.columns(2)
with col_titulo:
    st.title("🛰️ Monitoreo Satelital de Alta Definición (Google API)")
with col_boton:
    st.write("")
    st.write("")
    if st.button("🔄 Actualizar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Extracción limpia y directa del token privado desde los secretos
try:
    # Se extrae directamente sin operaciones de reemplazo que puedan dañar la firma de la clave
    GOOGLE_MAPS_API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"].strip()
except Exception:
    st.error("🚨 Error: No se encontró la clave 'GOOGLE_MAPS_API_KEY' en los Secrets de Streamlit.")
    GOOGLE_MAPS_API_KEY = ""

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

    # 3. GENERACIÓN DEL MAPA EMBED OFICIAL REGLAMENTARIO DE GOOGLE MAPS (SOLUCIONADO)
    if not df_f.empty and GOOGLE_MAPS_API_KEY != "":
        # Calculamos la media de tus coordenadas para situar la cámara exactamente sobre tus rutas
        lat_centro = str(df_f['LAT_INIOC'].mean())
        lon_centro = str(df_f['LON_INIOC'].mean())

        # URL MAESTRA OFICIAL CORREGIDA: Endpoint 'v1/place' oficial para mapas incrustados comerciales
        url_base = "https://google.com"
        url_embed_final = f"{url_base}?key={GOOGLE_MAPS_API_KEY}&q={lat_centro},{lon_centro}&zoom=17&maptype=satellite"

        # Dibujar iframe comercial oficial de Google Maps autorizado sin bloqueos
        st.markdown(
            f'<iframe width="100%" height="600" style="border:0; border-radius:8px;" allowfullscreen src="{url_embed_final}"></iframe>', 
            unsafe_allow_html=True
        )

        # Tabla inferior de registros
        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, use_container_width=True)
    else:
        if GOOGLE_MAPS_API_KEY == "":
            st.warning("⚠️ Esperando la configuración de la clave GOOGLE_MAPS_API_KEY dentro de los secretos de Streamlit.")
        else:
            st.warning("⚠️ No se encontraron coordenadas válidas para la combinación de filtros seleccionada.")

except Exception as e:
    st.error(f"🚨 Error crítico en el procesamiento: {e}")
