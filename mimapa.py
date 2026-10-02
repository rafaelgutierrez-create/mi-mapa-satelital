import streamlit as st
import pandas as pd
import pydeck as pdk
import time
import urllib.request
import io

st.set_page_config(layout="wide", page_title="Monitoreo Satelital Real")

# Título y botón alineados con la sintaxis moderna
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

    # Panel de filtros simplificado en columnas (Idéntico a tu lógica)
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
        # Calcular el centro geográfico dinámico
        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        # CONFIGURACIÓN DE PYDECK: Forzamos la capa satelital aérea libre de restricciones
        view_state = pdk.ViewState(
            latitude=lat_centro,
            longitude=lon_centro,
            zoom=15,
            pitch=0
        )

        # Dibujamos los puntos celestes interactivos
        layer = pdk.Layer(
            "ScatterplotLayer",
            df_f,
            get_position="[LON_INIOC, LAT_INIOC]",
            get_color="[0, 255, 255, 200]",  # Celeste brillante con transparencia
            get_radius=15,                  # Tamaño fijo en metros en la vida real
            pickable=True,
        )

        # Usamos el servidor de mapas oficial híbrido para pintar los techos reales de las casas
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_provider="carto",
            map_style="https://cartocdn.com", # Capa base de respaldo
            # Inyección de mosaicos satelitales directamente sobre el motor de renderizado gráfico de Streamlit
            views=[pdk.View(type="MapView", controller=True)],
        )

        # Cargar el mapa satelital directo de Google sin pasar por intermediarios de Plotly
        st.pydeck_chart(pdk.Deck(
            map_style=None,
            initial_view_state=view_state,
            layers=[
                # Capa ráster satelital real integrada directamente
                pdk.Layer(
                    "TileLayer",
                    "https://google.com{x}&y={y}&z={z}",
                    tile_size=256
                ),
                layer
            ],
            tooltip={"text": "Usuario: {ENC_USER}\nSegmento: {SEG}\nFecha: {FECHAOC}"}
        ))

        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, width='stretch')
    else:
        st.warning("⚠️ No se encontraron coordenadas para la combinación de filtros seleccionada.")

except Exception as e:
    st.error(f"🚨 Error de procesamiento: {e}")
