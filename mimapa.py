import plotly.express as px

# 1. Creamos unos datos de ejemplo (Sustitúyelos por tu DataFrame real)
# Ej: Coordenadas del centro de Madrid, España
data = {
    "lat": [40.4167, 40.4190, 40.4120],
    "lon": [-3.7037, -3.7050, -3.7010],
    "nombre": ["Punto A", "Punto B", "Punto C"],
}

# 2. Inicializamos la figura usando la función moderna para MapLibre (*_map)
fig = px.scatter_map(
    data,
    lat="lat",
    lon="lon",
    hover_name="nombre",
    size_max=15,
    zoom=13,  # Zoom inicial
)

# 3. Aplicamos la configuración estricta para la capa ráster de satélite
fig.update_layout(
    map={
        "style": "white-bg",  # Canvas limpio de fondo
        "layers": [
            {
                "sourcetype": "raster",  # Define el origen como imágenes ráster
                "type": "raster",  # CRÍTICO: Obliga a MapLibre a renderizarlo como texturas de mapa
                "below": "traces",  # Envía el satélite AL FONDO (detrás de tus puntos/líneas)
                "source": [
                    # URL del servidor de satélite de Google Maps (soporta zoom extremo)
                    "https://google.com{x}&y={y}&z={z}"
                    # NOTA: Si prefieres HÍBRIDO (Satélite + calles/nombres), cambia el "lyrs=s" por "lyrs=y"
                ],
            }
        ],
    },
    margin={"r": 0, "t": 0, "l": 0, "b": 0},  # Elimina márgenes para usar pantalla completa
)

# 4. Mostramos el mapa interactivo
fig.show()
