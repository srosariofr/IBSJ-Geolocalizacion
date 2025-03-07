import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
import osmnx as ox
import numpy as np
from shapely.geometry import Point
from sklearn.cluster import KMeans
from streamlit_folium import folium_static


# Cargar puntos de ejemplo
gdf = pd.read_csv('data.csv')
geometry = [Point(xy) for xy in zip(gdf["lng"], gdf["lat"])]  # Crea los puntos
gdf = gpd.GeoDataFrame(gdf, geometry=geometry, crs="EPSG:4326")  # Asigna CRS WGS84

# Sidebar: Parámetro de K-Means
n_clusters = st.sidebar.slider("Número de Clusters", min_value=2, max_value=10, value=3)

def get_cluster_color(cluster_label):
    colors = [
        'purple', 'black', 'cadetblue', 'pink', 'red', 'blue', 'darkgreen', 
        'darkred', 'lightgreen', 'orange', 'beige', 'darkpurple', 'darkblue', 'green', 'gray', 'lightgray', 'lightred', 'lightblue'
    ]
    return colors[cluster_label]

# Aplicar K-Means
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
coordinates = np.array([(point.y, point.x) for point in gdf.geometry])
gdf["cluster"] = kmeans.fit_predict(coordinates)

# 📊 Calcular estadísticas
cluster_counts = gdf["cluster"].value_counts().reset_index()
cluster_counts.columns = ["cluster", "cantidad"]
cluster_counts["porcentaje"] = (cluster_counts["cantidad"] / cluster_counts["cantidad"].sum()) * 100
cluster_counts["color"] = cluster_counts["cluster"].apply(get_cluster_color)

# 📌 Ordenar de mayor a menor
cluster_counts = cluster_counts.sort_values(by="cantidad", ascending=False)

# 📊 Mostrar tabla en la barra lateral
st.sidebar.subheader("📈 Estadísticas de Clustering")
st.sidebar.dataframe(cluster_counts.style.format({"porcentaje": "{:.2f}%"}), use_container_width=True)

# Crear el mapa
mapa = folium.Map(location=[18.5, -69.9], zoom_start=9)

for idx, row in gdf.iterrows():
    popup_text = f"""
    <b>Dirección Original:</b> {row["address_1"]}<br>
    <b>Nombre:</b> {row["first_name"]}<br>
    <b>Apellido:</b> {row["last_name"]}<br>
    <b>Calle:</b> {row["calle"]}<br>
    <b>Número:</b> {row["numero"]}<br>
    <b>Barrio:</b> {row["barrio"]}<br>
    <b>Ciudad:</b> {row["poligono"]}<br>
    <b>País:</b> {row["pais"]}<br>
    <b>Código Postal:</b> {row["codigo_postal"]}<br>
    <b>Cluster:</b> {row["cluster"]}
    """

    marker_color = get_cluster_color(row['cluster'])
    
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],  # Latitud, Longitud
        popup=folium.Popup(popup_text, max_width=300),  # Información al hacer clic
        tooltip=row["address_1"],  # Muestra la dirección al pasar el mouse
        icon=folium.Icon(color=marker_color, icon="info-sign")  # Color y estilo del marcador
    ).add_to(mapa)

# Mostrar el mapa en Streamlit
folium_static(mapa)
