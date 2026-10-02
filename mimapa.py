import streamlit as st
import pandas as pd
import requests
import io
import json

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Monitoreo Satelital Real HD")

# Título y botón de actualización manual alineados (Sintaxis corregida para v2026)
col_titulo, col_boton = st.columns(2)
with col_titulo:
    st.title("🛰️ Monitoreo Satelital de Alta Definición (Google API)2")
with col_boton:
    st.write("")
    st.write("")
    if st.button("🔄 Actualizar Datos", width='stretch'):
        st.cache_data.clear()
        st.rerun()

# Extracción de tu API Key guardada en Streamlit.io
try:
    GOOGLE_MAPS_API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
except Exception:
    st.error("🚨 Error: No se encontró la clave 'GOOGLE_MAPS_API_KEY' en los Secrets de Streamlit.")
    GOOGLE_MAPS_API_KEY = ""

# TU ENLACE REAL DE GOOGLE SHEETS FIXED
URL_DE_TU_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSXnTLmB6L7QK4Tj33d016VUUD419vBnbgdQYrOHHQzJc_74VDSqDWdh3bQSrSF8oKKHjEZ5bl6PxAK/pub?gid=0&single=true&output=csv"


@st.cache_data(ttl=2)
def cargar_datos():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(URL_DE_TU_SHEET, headers=headers, timeout=15)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    
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

    # 3. COMPONENTE MAPA PREMIUM CON BASE DE DATOS INYECTADA EN LÍNEA
    if not df_f.empty and GOOGLE_MAPS_API_KEY != "":
        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        # Empaquetamos la lista de coordenadas directamente desde el servidor Python
        puntos_lista = []
        for _, fila in df_f.iterrows():
            puntos_lista.append({
                "lat": float(fila['LAT_INIOC']),
                "lng": float(fila['LON_INIOC']),
                "info": f"<b>Usuario:</b> {fila['ENC_USER']}<br><b>Segmento:</b> {fila['SEG']}<br><b>Sujeto:</b> {fila['SbjNum']}"
            })
        json_puntos = json.dumps(puntos_lista)

        # Mapa HTML embebido puro compatible con las restricciones del navegador de Streamlit Cloud
        html_mapa = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                #map {{ height: 100%; width: 100%; position: absolute; top: 0; left: 0; }}
                html, body {{ height: 100%; margin: 0; padding: 0; }}
            </style>
            <script>
                function initMap() {{
                    var centro = {{ lat: {lat_centro}, lng: {lon_centro} }};
                    var map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: 16,
                        center: centro,
                        mapTypeId: google.maps.MapTypeId.HYBRID, // Satélite e Infraestructura HD integrados
                        maxZoom: 22, // Desbloquea el acercamiento máximo absoluto a nivel de patio/casa
                        tilt: 0
                    }});

                    var puntos = {json_puntos};
                    var infowindow = new google.maps.InfoWindow();

                    puntos.forEach(function(punto) {{
                        var marker = new google.maps.Marker({{
                            position: {{ lat: punto.lat, lng: punto.lng }},
                            map: map,
                            icon: {{
                                path: google.maps.SymbolPath.CIRCLE,
                                fillColor: '#00FFFF',
                                fillOpacity: 0.9,
                                strokeColor: '#FFFFFF',
                                strokeWeight: 1.5,
                                scale: 7
                            }}
                        }});

                        marker.addListener('click', function() {{
                            infowindow.setContent(punto.info);
                            infowindow.open(map, marker);
                        }});
                    }});
                }}
            </script>
            <script src="https://googleapis.com{GOOGLE_MAPS_API_KEY}&callback=initMap" async defer></script>
        </head>
        <body>
            <div id="map"></div>
        </body>
        </html>
        """
        
        # Renderizado del mapa en el bloque web
        st.components.v1.html(html_mapa, height=650, scrolling=False)

        # Tabla de registros inferior
        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, width='stretch')
    else:
        if GOOGLE_MAPS_API_KEY == "":
            st.warning("⚠️ Esperando la configuración de la clave GOOGLE_MAPS_API_KEY en los secretos de Streamlit.")
        else:
            st.warning("⚠️ No se encontraron coordenadas válidas para los filtros aplicados.")

except Exception as e:
    st.error(f"🚨 Error crítico en el procesamiento: {e}")
