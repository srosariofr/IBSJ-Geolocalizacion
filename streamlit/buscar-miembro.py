import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point
from streamlit_folium import folium_static


st.title("🔍 Buscar Miembros Cercanos")

# Cargar los datos de coordenadas
@st.cache_data
def cargar_puntos():
    df = pd.read_csv("data.csv")  # Asegúrate de que el archivo existe
    geometry = [Point(xy) for xy in zip(df["lng"], df["lat"])]
    return gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

gdf = cargar_puntos()

# 📌 Permitir búsqueda por ID, nombre o apellido
criterio = st.text_input("Ingrese ID, nombre o apellido:")

if criterio:
    # Filtrar coincidencias
    coincidencias = gdf[
        (gdf["id"].astype(str).str.contains(criterio, case=False, na=False)) |
        (gdf["first_name"].str.contains(criterio, case=False, na=False)) |
        (gdf["last_name"].str.contains(criterio, case=False, na=False))
    ]
    
    if len(coincidencias) == 0:
        st.warning("❌ No se encontraron coincidencias.")
    else:
        miembro = None
        if len(coincidencias) > 1:
            # Si hay varias coincidencias, pedir al usuario que seleccione una
            seleccion = st.selectbox("Selecciona un miembro:", coincidencias["first_name"] + " " + coincidencias["last_name"])
            miembro = coincidencias[coincidencias["first_name"] + " " + coincidencias["last_name"] == seleccion].iloc[0]
        else:
            miembro = coincidencias.iloc[0]
        
        # Mostrar la información del miembro seleccionado
        st.success(f"✅ Miembro seleccionado: {miembro['first_name']} {miembro['last_name']}")
        
        # Obtener ubicación del miembro
        lat, lng = miembro.geometry.y, miembro.geometry.x
        
        # 📌 Filtrar los puntos dentro de un radio de 1 km
        gdf["distancia"] = gdf.geometry.distance(Point(lng, lat)) * 111  # Convertir grados a km
        cercanos = gdf[gdf["distancia"] <= 1]  # Puntos dentro de 1 km
        
        # 📌 Crear el mapa centrado en el miembro
        mapa = folium.Map(location=[lat, lng], zoom_start=14)

        # 📌 Marcar el punto del miembro en rojo
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(f"""
                <b>Nombre:</b> {miembro["first_name"]} {miembro["last_name"]}<br>
                <b>Dirección:</b> {miembro["address_1"]}
                """, max_width= 300), # Muestra la dirección al pasar el mouse
            icon=folium.Icon(color="red", icon="info-sign")  # Color y estilo del marcador
        ).add_to(mapa)

        # 📌 Marcar puntos cercanos en azul
        for _, row in cercanos.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x], radius=6, color="blue", fill=True, fill_color="blue",
                fill_opacity=0.9, 
                popup=folium.Popup(f"""
                    <b>Nombre:</b> {row["first_name"]} {row["last_name"]}<br>
                    <b>Dirección:</b> {row["address_1"]}
                    """, max_width=300),
            ).add_to(mapa)

        # 📌 Mostrar el mapa en Streamlit
        folium_static(mapa, width=900, height=600)
        st.subheader("💡 Miembros Cercanos")
        st.write(cercanos[['id', 'first_name', 'last_name', 'address_1', 'address_2', 'barrio', 'poligono']])
