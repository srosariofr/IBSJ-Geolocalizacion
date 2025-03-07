import streamlit as st

# Define the pages
main_page = st.Page("app.py", title="Geolocalización Miembros IBSJ", icon="🏠")
page_2 = st.Page("buscar-miembro.py", title="Buscar Miembros Cercanos", icon="🔍")

# Set up navigation
pg = st.navigation([main_page, page_2])

# Run the selected page
pg.run()