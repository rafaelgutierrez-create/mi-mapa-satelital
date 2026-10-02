import streamlit as st
import pandas as pd
import requests
import io
import json

# 1. Configurar la página en modo ancho
st.set_page_config(layout="wide", page_title="Monitoreo Satelital Real HD")

# Título y botón de actualización manual alineados (Línea 11 corregida)
col_titulo, col_boton = st.columns(2)
with col_titulo:
    st.title("🛰️ Monitoreo Satelital de Alta Definición (Google API)")
with col_boton:
    st.write("")
    st.write("")
    if st.button("🔄 Actualizar Datos", width='stretch'):
        st.cache_data.clear()
        st.rerun()

# 🔑 EXTRACCIÓN SEGURA DE TU API KEY DE GOOGLE DESDE LOS SECRETOS DE STREAMLIT
try:
    GOOGLE_MAPS_API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
except Exception:
    st.error("🚨 Error: No se encontró la clave 'GOOGLE_MAPS_API_KEY' en los Secrets de Streamlit.")
    GOOGLE_MAPS_API_KEY = ""

# TU ENLACE REAL DE GOOGLE SHEETS
URL_DE_TU_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSXnTLmB6L7QK4Tj33d016VUUD419vBnbgdQYrOHHQzJc_74VDSqDWdh3bQSrSF8oKKHjEZ5bl6PxAK/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=2)
def cargar_datos():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL_DE_TU_SHEET, headers=headers, timeout=15)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    
    # Limpieza estricta de coordenadas
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

    # 3. CONSTRUCCIÓN DEL MAPA PREMIUM DE GOOGLE MAPS JAVASCRIPT API
    if not df_f.empty and GOOGLE_MAPS_API_KEY != "":
        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        # Convertimos los puntos de tu tabla a formato JSON para pasárselos al mapa
        puntos_lista = []
        for _, fila in df_f.iterrows():
            puntos_lista.append({
                "lat": float(fila['LAT_INIOC']),
                "lng": float(fila['LON_INIOC']),
                "info": f"Usuario: {fila['ENC_USER']}<br>Segmento: {fila['SEG']}<br>Sujeto: {fila['SbjNum']}"
            })
        json_puntos = json.dumps(puntos_lista)

        # CÓDIGO HTML/JAVASCRIPT NATIVO DE GOOGLE MAPS
        html_mapa = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                #map {{ height: 100%; width: 100%; position: absolute; top: 0; left: 0; }}
                html, body {{ height: 100%; margin: 0; padding: 0; }}
            </style>
            <script src="https://googleapis.com{GOOGLE_MAPS_API_KEY}"></script>
            <script>
                function initMap() {{
                    var centro = {{ lat: {lat_centro}, lng: {lon_centro} }};
                    
                    // Inicializamos el mapa en modo satélite híbrido nativo (HYBRID)
                    var map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: 17,
                        center: centro,
                        mapTypeId: 'hybrid', // <--- Fuerza las fotos satelitales oficiales de Google
                        maxZoom: 21,         // Permite el zoom más profundo del mundo sin ponerse en blanco
                        tilt: 0
                    }});

                    var puntos = {json_puntos};
                    var infowindow = new google.maps.InfoWindow();

                    // Dibujar cada marcador interactivo
                    puntos.forEach(function(punto) {{
                        var marker = new google.maps.Marker({{
                            position: {{ lat: punto.lat, lng: punto.lng }},
                            map: map,
                            icon: {{
                                path: google.maps.SymbolPath.CIRCLE,
                                fillColor: '#00FFFF',
                                fillOpacity: 0.9,
                                strokeColor: '#FFFFFF',
                                strokeWeight: 2,
                                scale: 8
                            }}
                        }});

                        // Ventana de información al hacer clic en el punto
                        marker.addListener('click', function() {{
                            infowindow.setContent(punto.info);
                            infowindow.open(map, marker);
                        }});
                    }});
                }}
                window.onload = initMap;
            </script>
        </head>
        <body>
            <div id="map"></div>
        </body>
        </html>
        """
        
        # Desplegar el mapa premium de forma directa
        st.components.v1.html(html_mapa, height=650)

        # Tabla inferior de registros
        st.subheader("📊 Registros en Pantalla")
        st.dataframe(df_f, width='stretch')
    else:
        if GOOGLE_MAPS_API_KEY == "":
            st.warning("⚠️ Esperando la configuración de la clave GOOGLE_MAPS_API_KEY en los secretos de Streamlit.")
        else:
            st.warning("⚠️ No se encontraron coordenadas válidas para la combinación de filtros seleccionada.")

except Exception as e:
    st.error(f"🚨 Error crítico en el procesamiento: {e}")
