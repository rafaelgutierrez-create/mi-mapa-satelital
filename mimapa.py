import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
from streamlit_folium import st_folium
import folium

# 1. Configurar la página en modo ancho y tema del Tablero
st.set_page_config(layout="wide", page_title="Tablero de Control Satelital")

# Título de la Plataforma y Botón de actualización
col_titulo, col_boton = st.columns(2)
with col_titulo:
    st.title("🛰️ Sistema de Auditoría y Monitoreo Satelital Pro")
with col_boton:
    st.write("")
    st.write("")
    if st.button("🔄 Actualizar Servidor", width='stretch'):
        st.cache_data.clear()
        st.rerun()

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

    # 2. PANEL DE FILTROS EN MODALIDAD MULTISELECCIÓN
    st.subheader("🎛️ Panel de Filtros Múltiples (Puedes elegir varios a la vez)")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        usuarios_lista = sorted(list(df['ENC_USER'].dropna().unique()))
        user_sel = st.multiselect("Usuarios (ENC_USER):", usuarios_lista, placeholder="Todos los usuarios")
    if user_sel: # Si selecciona uno o varios, filtra por esa lista
        df_f = df_f[df_f['ENC_USER'].isin(user_sel)]

    with col2:
        fechas_lista = sorted(list(df_f['FECHAOC'].dropna().astype(str).unique()))
        fecha_sel = st.multiselect("Fechas (FECHAOC):", fechas_lista, placeholder="Todas las fechas")
    if fecha_sel:
        df_f = df_f[df_f['FECHAOC'].astype(str).isin(fecha_sel)]

    with col3:
        segmentos_lista = sorted(list(df_f['SEG'].unique()))
        seg_sel = st.multiselect("Segmentos (SEG):", segmentos_lista, placeholder="Todos los segmentos")
    if seg_sel:
        df_f = df_f[df_f['SEG'].isin([int(x) for x in seg_sel])]

    with col4:
        sujetos_lista = sorted(list(df_f['SbjNum'].unique()))
        sbj_sel = st.multiselect("Sujetos (SbjNum):", sujetos_lista, placeholder="Todos los sujetos")
    if sbj_sel:
        df_f = df_f[df_f['SbjNum'].isin([int(x) for x in sbj_sel])]

    # Interruptor para activar la auditoría visual de caminos
    mostrar_lineas = st.checkbox("🗺️ Activar Líneas de Ruta y Secuencia de Auditoría (Inicio/Fin)")

    st.markdown("---")

    # 3. SECCIÓN DE MÉTRICAS DINÁMICAS (KPIs)
    st.subheader("📊 Indicadores Operacionales del Filtro")
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Total Formularios Recolectados", len(df_f))
    with m_col2:
        st.metric("Encuestadores en Terreno", df_f['ENC_USER'].nunique())
    with m_col3:
        st.metric("Segmentos Cubiertos", df_f['SEG'].nunique())

    st.markdown("---")

    # 4. GENERACIÓN DEL MAPA SATELITAL PREMIUM DE GOOGLE
    if not df_f.empty:
        lat_centro = df_f['LAT_INIOC'].mean()
        lon_centro = df_f['LON_INIOC'].mean()

        m = folium.Map(location=[lat_centro, lon_centro], zoom_start=16, control_scale=True)

        # Inyección directa del servidor satelital híbrido de Google (Fotos + Calles)
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            attr="Google Maps Satellite Hybrid",
            name="Google Satélite Híbrido",
            max_zoom=20, 
            overlay=False,
            control=False
        ).add_to(m)

        # Lógica avanzada para trazar rutas y detectar extremos (Inicio/Fin)
        if mostrar_lineas:
            grupos = df_f.groupby(['ENC_USER', 'FECHAOC'])
            for (usuario, fecha), grupo in grupos:
                grupo_ordenado = grupo.sort_values(by='SbjNum')
                coordenadas_ruta = grupo_ordenado[['LAT_INIOC', 'LON_INIOC']].values.tolist()
                
                if len(coordenadas_ruta) > 1:
                    folium.PolyLine(
                        locations=coordenadas_ruta,
                        color="#FFFF00",
                        weight=3,
                        opacity=0.8,
                        tooltip=f"Trayecto de: {usuario} ({fecha})"
                    ).add_to(m)

        # Dibujar marcadores con lógica de semáforo e índices correlativos
        df_f = df_f.sort_values(by=['ENC_USER', 'FECHAOC', 'SbjNum'])
        df_f['Parada_Num'] = df_f.groupby(['ENC_USER', 'FECHAOC']).cumcount() + 1

        for _, fila in df_f.iterrows():
            user_actual = fila['ENC_USER']
            fecha_actual = fila['FECHAOC']
            parada_idx = fila['Parada_Num']
            
            total_paradas_grupo = len(df_f[(df_f['ENC_USER'] == user_actual) & (df_f['FECHAOC'] == fecha_actual)])

            # Color amarillo intenso por defecto
            color_punto = "#FFFF00"
            leyenda_auditoria = f"Parada #{parada_idx}"

            if mostrar_lineas:
                if parada_idx == 1:
                    color_punto = "#00FF00"  # Verde de inicio (puedes cambiarlo aquí)
                    leyenda_auditoria = "🚩 PUNTO DE INICIO"
                elif parada_idx == total_paradas_grupo and total_paradas_grupo > 1:
                    color_punto = "#FF3333"  # Rojo de fin
                    leyenda_auditoria = "🏁 PUNTO FINAL"

            texto_popup = f"""
            <b>🕵️ Estado:</b> {leyenda_auditoria}<br>
            <b>Usuario:</b> {user_actual}<br>
            <b>Fecha:</b> {fecha_actual}<br>
            <b>Segmento:</b> {fila['SEG']}<br>
            <b>Sujeto (SbjNum):</b> {fila['SbjNum']}
            """
            
            texto_tooltip = f"{leyenda_auditoria} | Sujeto: {fila['SbjNum']}"
            
            folium.CircleMarker(
                location=[fila['LAT_INIOC'], fila['LON_INIOC']],
                radius=3,
                popup=folium.Popup(texto_popup, max_width=250),
                tooltip=folium.Tooltip(texto_tooltip, permanent=False),
                color=color_punto,
                fill=True,
                fill_color=color_punto,
                fill_opacity=0.9
            ).add_to(m)

        # Renderizar mapa en la pantalla
        st_folium(m, width=1400, height=600, returned_objects=[])

        # 5. TABLA DE REGISTROS Y BOTÓN DE DESCARGA
        st.markdown("---")
        col_sub, col_descarga = st.columns(2)
        with col_sub:
            st.subheader("📋 Registros de Datos en Pantalla")
        with col_descarga:
            csv_data = df_f.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Lista a Excel (CSV)",
                data=csv_data,
                file_name="reporte_coordenadas_filtrado.csv",
                mime="text/csv",
                width='stretch'
            )
        
        st.dataframe(df_f.drop(columns=['Parada_Num']), width='stretch')

        # 6. GRÁFICO ESTADÍSTICO DE PRODUCTIVIDAD (PLOTLY BARS)
        st.markdown("---")
        st.subheader("📊 Productividad General por Encuestador")
        
        df_conteo = df_f['ENC_USER'].value_counts().reset_index()
        df_conteo.columns = ['Encuestador', 'Formularios Levantados']
        
        fig_barras = px.bar(
            df_conteo, 
            x='Encuestador', 
            y='Formularios Levantados',
            text='Formularios Levantados',
            color='Encuestador',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_barras.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=350)
        st.plotly_chart(fig_barras, width='stretch')

    else:
        st.warning("⚠️ No se encontraron coordenadas válidas para los filtros seleccionados.")

except Exception as e:
    st.error(f"🚨 Error crítico en el procesamiento: {e}")
