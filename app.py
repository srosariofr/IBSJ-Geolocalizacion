import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
import osmnx as ox
from shapely.geometry import Point
from sklearn.cluster import KMeans
from streamlit_folium import folium_static

# Cargar los polígonos de la ciudad
@st.cache_data
def cargar_poligonos():
    return ox.features_from_place("Santo Domingo, Dominican Republic", {"boundary": "administrative", "admin_level": "10"})

gdf_poligonos = cargar_poligonos()

# Cargar puntos de ejemplo
puntos = [
    (-69.9, 18.5), (-70.0, 18.45), (-69.85, 18.55), (-69.92, 18.52), (-69.88, 18.48)
]
gdf_puntos = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in puntos], crs="EPSG:4326")

# Sidebar: Parámetro de K-Means
n_clusters = st.sidebar.slider("Número de Clusters", min_value=2, max_value=10, value=3)

# Aplicar K-Means
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
gdf_puntos["cluster"] = kmeans.fit_predict(gdf_puntos.geometry.apply(lambda p: [p.x, p.y]))

# Crear el mapa
mapa = folium.Map(location=[18.5, -69.9], zoom_start=12)
for _, row in gdf_poligonos.iterrows():
    if row.geometry is not None:
        folium.GeoJson(row.geometry, tooltip=row.get("name", "Barrio sin nombre"), style_function=lambda x: {"color": "blue"}).add_to(mapa)

# Agregar puntos al mapa con color por cluster
colors = ["red", "green", "blue", "purple", "orange", "pink", "brown", "gray", "cyan", "yellow"]
for _, row in gdf_puntos.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=6,
        color=colors[row.cluster % len(colors)],
        fill=True,
        fill_color=colors[row.cluster % len(colors)],
        fill_opacity=0.7,
    ).add_to(mapa)

# Mostrar el mapa en Streamlit
folium_static(mapa)
