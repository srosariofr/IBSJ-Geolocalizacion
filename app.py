import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
import osmnx as ox
from shapely.geometry import Point
from sklearn.cluster import KMeans
from streamlit_folium import folium_static


# Cargar puntos de ejemplo
gdf = pd.read_csv('data.csv')
geometry = [Point(xy) for xy in zip(gdf["lng"], gdf["lat"])]  # Crea los puntos
gdf = gpd.GeoDataFrame(gdf, geometry=geometry, crs="EPSG:4326")  # Asigna CRS WGS84

# Sidebar: Parámetro de K-Means
n_clusters = st.sidebar.slider("Número de Clusters", min_value=2, max_value=10, value=3)

# Aplicar K-Means
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
coordinates = np.array([(point.y, point.x) for point in gdf.geometry])
gdf["cluster"] = kmeans.fit_predict(coordinates)


# Crear el mapa
mapa = folium.Map(location=[18.5, -69.9], zoom_start=9)

# Agregar puntos al mapa con color por cluster
colors = ["red", "green", "blue", "purple", "orange", "pink", "brown", "gray", "cyan", "yellow"]
for _, row in gdf.iterrows():
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
