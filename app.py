import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
import osmnx as ox
import numpy as np
from shapely.geometry import Point
from sklearn.cluster import KMeans
from streamlit_folium import st_folium


st.set_page_config(
    page_title='Geolocalización Miembros IBSJ', 
    page_icon=None, 
    layout="wide", 
    initial_sidebar_state="auto", 
    menu_items=None
)

with st.container():
    st.header("Geolocalización Miembros IBSJ", divider="gray")
    col1, col2 = st.columns([0.3, 0.7], gap='small', border=True)

# Cargar puntos de ejemplo
@st.cache_data 
def load_data():
    gdf = pd.read_csv('data.csv')
    geometry = [Point(xy) for xy in zip(gdf["lng"], gdf["lat"])]  # Crea los puntos
    gdf = gpd.GeoDataFrame(gdf, geometry=geometry, crs="EPSG:4326")  # Asigna CRS WGS84
    return gdf

@st.cache_data 
def get_cluster_color(cluster_label):
    colors = [
        'purple', 'black', 'cadetblue', 'pink', 'red', 'blue', 'darkgreen', 
        'darkred', 'lightgreen', 'orange', 'beige', 'darkpurple', 'darkblue', 'green', 'gray', 'lightgray', 'lightred', 'lightblue'
    ]
    return colors[cluster_label]

# Sidebar: Parámetro de K-Means
with col1:
    n_clusters = st.slider("Selecciona número de Clusters:", min_value=2, max_value=10, value=3)


gdf = load_data()

# Aplicar K-Means
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
coordinates = np.array([(point.y, point.x) for point in gdf.geometry])
gdf["cluster"] = kmeans.fit_predict(coordinates)

# 📊 Calcular estadísticas
cluster_counts = gdf["cluster"].value_counts().reset_index()
cluster_counts.columns = ["cluster", "cantidad"]
cluster_counts["%"] = (cluster_counts["cantidad"] / cluster_counts["cantidad"].sum()) * 100
cluster_counts["color"] = cluster_counts["cluster"].apply(get_cluster_color)
cluster_counts = cluster_counts[['cluster', 'color', 'cantidad', '%']]

# 📌 Ordenar de mayor a menor
cluster_counts = cluster_counts.sort_values(by="cantidad", ascending=False)

# Crear el mapa
mapa = folium.Map(location=[18.5, -69.9], zoom_start=11)

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
with col2:
    st_folium(mapa, width="100%", returned_objects=[])

# 📊 Mostrar tabla 
with col1:
    st.subheader("📈 Resumen")
    cluster_counts.reset_index(drop=True, inplace=True)
    st.dataframe(cluster_counts.style.format({"%": "{:.1f}%"}), use_container_width=True)
