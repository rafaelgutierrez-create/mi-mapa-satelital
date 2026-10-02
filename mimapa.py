import plotly.express as px

# 1. Datos de prueba
data = {
    "lat": [40.4167, 40.4190, 40.4120],
    "lon": [-3.7037, -3.7050, -3.7010],
    "nombre": ["Punto A", "Punto B", "Punto C"],
}

fig = px.scatter_map(
    data,
    lat="lat",
    lon="lon",
    hover_name="nombre",
    zoom=13,
)

# 2. Sintaxis Oficial de Plotly Moderna (Evita que el lienzo quede en blanco)
fig.update_layout(
    map_style="white-bg",  # <--- Cambia a propiedad plana
    map_layers=[           # <--- Cambia a propiedad plana
        {
            "below": "traces",
            "sourcetype": "raster",
            "source": [
                "https://google.com{x}&y={y}&z={z}"
            ]
        }
    ],
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

fig.show()
