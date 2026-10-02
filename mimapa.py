import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import urllib.request
import io

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Monitoreo Satelital Real")

# Título y botón de actualización manual alineados
col_titulo, col_boton = st.columns([4, 1])
with col_titulo:
    st.title("Encuesta Coordenadas")
with col_boton:
    st.write("") 
    st.write("") 
    if st.button("🔄 Actualizar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Tu enlace de Google Sheets (Formato CSV)
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

    # 2. PANEL DE FILTROS EN COLUMNAS
    st.subheader("Filtros")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        usuarios = ["Todos"] + sorted(list(df['ENC_USER'].dropna().unique()))
        user_sel = st.selectbox("Usuario (ENC_USER):", usuarios)
        
    df_f = df.copy()
    if user_sel != "Todos":
        df_f = df_f[df_f['ENC_USER'] == user_sel]

    with col2:
        fechas = ["Todas"] + sorted(list(df_f['FECHAOC'].dropna().astype(str).unique()))
        fecha_sel = st.selectbox("Fecha (FECHAOC):", fechas)
    if fecha_sel != "Todas":
        df_f = df_f[df_f['FECHAOC'].astype(str) == fecha_sel]

    with col3:
        df_f['SEG'] = pd.to_numeric(df_f['SEG'], errors='coerce').fillna(0).astype(int)
        segmentos = ["Todos"] + sorted(list(df_f['SEG'].unique()))
        seg_sel = st.selectbox("Segmento (SEG):", segmentos)
    if seg_sel != "Todos":
        df_f = df_f[df_f['SEG'] == int(seg_sel)]

    with col4:
        df_f['SbjNum'] = pd.to_numeric(df_f['SbjNum'], errors='coerce').fillna(0).astype(int)
        sujetos = ["Todos"] + sorted(list(df_f['SbjNum'].unique()))
        sbj_sel = st.selectbox("Sujeto (SbjNum):", sujetos)
    if sbj_sel != "Todos":
        df_f = df_f[df_f['SbjNum'] == int(sbj_sel)]

    st.markdown("---")

    # 3. MAPA CON GRAPH OBJECTS (OPTIMIZADO PARA PRODUCCIÓN HTTPS)
    if not df_f.empty:
        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        fig = go.Figure(go.Scattermap(
            lat=df_f["LAT_INIOC"],
            lon=df_f["LON_INIOC"],
            mode='markers',
            marker=go.scattermap.Marker(size=14, color='red', opacity=0.9),
            text="Usuario: " + df_f["ENC_USER"].astype(str) + "<br>Sujeto: " + df_f["SbjNum"].astype(str),
            hoverinfo='text'
        ))

        fig.update_layout(
            map=dict(
                style="white-bg", 
                center=dict(lat=lat_centro, lon=lon_centro),
                zoom=15,
                layers=[{
                    "sourcetype": "raster",
                    "source": ["https://google.com{x}&y={y}&z={z}"],
                    "sourceattribution": "Google"
                }]
            ),
            margin={"r":0,"t":0,"l":0,"b":0},
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Registros")
        st.dataframe(df_f, use_container_width=True)
    else:
        st.warning("⚠️ No se encontraron coordenadas para la combinación de filtros seleccionada.")

except Exception as e:
    st.error(f"Error procesando la información: {e}")
