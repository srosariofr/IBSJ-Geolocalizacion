import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point
from streamlit_folium import folium_static
from unidecode import unidecode


st.title("🔍 Buscar Miembros Cercanos")

# Cargar los datos de coordenadas
@st.cache_data
def cargar_puntos():
    return gpd.read_file("geolocations.db", encoding='latin-1')

gdf = cargar_puntos()

# 📌 Permitir búsqueda por ID, nombre o apellido
criterio = st.text_input("Ingrese ID, nombre o apellido:", "")
buscar = st.button("🔍 Buscar")

def normalizar_texto(texto):
    return unidecode(texto).lower() if isinstance(texto, str) else ""
    
# 📌 Inicializar session_state para búsqueda y selección
if "coincidencias" not in st.session_state:
    st.session_state.coincidencias = None
if "miembro_seleccionado" not in st.session_state:
    st.session_state.miembro_seleccionado = None


if buscar and criterio:
    criterio_norm = normalizar_texto(criterio)

    coincidencias = gdf[
        (gdf["id"].astype(str).apply(normalizar_texto).str.contains(criterio_norm, case=False, na=False)) |
        (gdf["first_name"].apply(normalizar_texto).str.contains(criterio_norm, case=False, na=False)) |
        (gdf["last_name"].apply(normalizar_texto).str.contains(criterio_norm, case=False, na=False))
    ]
    
    if len(coincidencias) == 0:
        st.warning("❌ No se encontraron coincidencias.")
        st.session_state.coincidencias = None
        st.session_state.miembro_seleccionado = None
    else:
        st.session_state.coincidencias = coincidencias
        st.session_state.miembro_seleccionado = None  # Reiniciar selección al buscar nuevamente
        
        
# 📌 Si hay coincidencias, mostrar selectbox
if st.session_state.coincidencias is not None:
    coincidencias = st.session_state.coincidencias

    if len(coincidencias) == 1:
        miembro = coincidencias.iloc[0]
    else:
        seleccion = st.selectbox(
            "Selecciona un miembro:",
            coincidencias["first_name"] + " " + coincidencias["last_name"],
            key="seleccion_usuario",
        )
        miembro = coincidencias[
            (coincidencias["first_name"] + " " + coincidencias["last_name"]) == seleccion
        ].iloc[0]

    st.session_state.miembro_seleccionado = miembro


# 📌 Mostrar mapa si hay un miembro seleccionado
if st.session_state.miembro_seleccionado is not None:
    miembro = st.session_state.miembro_seleccionado
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
    folium_static(mapa, width=600, height=300)
    st.subheader(f"💡 Miembros Cercanos a: {miembro['first_name']} {miembro['last_name']}")
    st.write(cercanos[['id', 'first_name', 'last_name', 'address_1', 'address_2', 'barrio', 'poligono']])
