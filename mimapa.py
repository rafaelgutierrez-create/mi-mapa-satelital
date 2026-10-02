import streamlit as st
import pydeck as pdk
import pandas as pd

# Datos de prueba
chart_data = pd.DataFrame({
   'lat': [40.4167, 40.4190, 40.4120],
   'lon': [-3.7037, -3.7050, -3.7010]
})

# Configurar el mapa satelital nativo en Pydeck
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/satellite-v9', # Estilo satélite nativo autorizado
    initial_view_state=pdk.ViewState(
        latitude=40.4167,
        longitude=-3.7037,
        zoom=13,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=chart_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=100,
        ),
    ],
))
