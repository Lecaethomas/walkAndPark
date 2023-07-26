import os
import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import folium_static

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the result GeoDataFrame from the shapefile
result_shapefile_path = os.path.join(current_dir, "data", "grid_walk_results.shp")  # Change the file name to your polygons shapefile
result_gdf = gpd.read_file(result_shapefile_path)

# Load the park GeoDataFrame from the shapefile
park_shapefile_path = os.path.join(current_dir, "data", "public_parks_.shp")
park_gdf = gpd.read_file(park_shapefile_path)

# Create a folium map centered at the centroid of the first polygon in result_gdf
m = folium.Map(location=[result_gdf["geometry"].centroid.y.mean(), result_gdf["geometry"].centroid.x.mean()], zoom_start=12)

# Create a colormap for the walking times (gradient of reds)
min_walking_time = result_gdf["walking_ti"].min()
max_walking_time = result_gdf["walking_ti"].max()
color_scale = folium.LinearColormap(colors=['#ffffd4', '#fed98e', '#fe9929', '#d95f0e', '#993404'], vmin=min_walking_time, vmax=max_walking_time)

# Create a folium layer for the parks
parks_layer = folium.FeatureGroup(name="Parcs")

# Add park polygons to the parks_layer
for idx, row in park_gdf.iterrows():
    park_id = row["id"]
    park_polygon = row.geometry
    folium.GeoJson(
        park_polygon.__geo_interface__,
        style_function=lambda x: {"fillColor": "transparent", "color": "blue", "weight": 2},
        tooltip=f"Identifiant du parc: {park_id}",
        name=f"Park {park_id}",
    ).add_to(parks_layer)

# Create another folium layer for the walking times
walk_times_layer = folium.FeatureGroup(name="Temps à pieds")

# Add the polygons with walking times to the walk_times_layer
for idx, row in result_gdf.iterrows():
    polygon = row.geometry
    walking_time = row["walking_ti"]
    park_cor = row["park_id"]
    folium.GeoJson(
        polygon.__geo_interface__,
        style_function=lambda x, walking_time=walking_time: {
            "fillColor": color_scale(walking_time),
            "color": color_scale(walking_time),
            "weight": 2,
            "fillOpacity": 0.7,
        },
        tooltip=f"Temps à pieds {walking_time} secondes  <br> Identifiant du parc correspondant : {park_cor}",
    ).add_to(walk_times_layer)

# Add the parks_layer and walk_times_layer to the map
parks_layer.add_to(m)
walk_times_layer.add_to(m)

# Add the colormap to the map
color_scale.caption = "Temps à pieds (secondes)"
color_scale.add_to(m)

# Add the layer control to the map
folium.LayerControl().add_to(m)


############ TEXT
# Add a title to the app
st.title("Tentative de modélisation de l'accessibilité des parcs urbains toulousains")
st.subheader("Quoi? :deciduous_tree:" )

# Add some normal text describing the map
st.write("Cette carte montre l'accessibilité à des parcs calculée pour des personnes non-PMR depuis le centre des carrés vers les points représentant les parcs. Les carreaux font 200m*200m et correspondent à la base de données Filosofi de l'INSEE filtrée sur la commune de Toulouse. Cette base de données fournit différents indicateurs socio-économiques à l'échelle de cette unité qu'est le carreau. Un carreau signifie la présence de ménages mais suffisamment nombreux pour garantir leur anonymat.")
st.write("Les temps de déplacements sont représentés en utilisant une échelle de couleurs allant du jaune au marron, la première correspondant à un temps cours, la deuxième à un temps long.")

# Display the folium map in the Streamlit app using streamlit_folium's folium_static function
folium_static(m)

st.write("Au delà de la question de l'accessibilité à la ressource spécifique que sont les espaces verts, ce type d'analyse peut être conduit pour tous types de données (Base Permanente des Equipements, BD Topo ...) et permettre ainsi d'avoir un aperçut de la dotation des territoires en équipements ainsi que leur accessibilité voir d'aborder le [concept de la ville du 1/4 d'heure](https://www.moreno-web.net/wordpress/wp-content/uploads/2020/12/Livre-Blanc-2-Etude-ville-quart-heure-18.12.2020.pdf).")

st.subheader("Comment? :question:" )
st.write("Techniquement le principe derrière cette modélisation est que l'on récupère le centroïde de chaque carreau, pour ensuite faire appel à l'API overpass (données OSM) permettant de récupérer les polygones correspondant aux parcs (leisure = parks) dans un rayon de 1km autour de chaque point.")
st.write("L'algorithme fait ensuite appel à l'OSRM (Open Source Routing Machine) pour chaque point et les parcs correspondants pour calculer le temps nécessaire pour les rejoindre à pieds. On peut ensuite extraire le parc le plus proche (en temps de marche) ainsi que le temps nécessaire pour s'y rendre.")

st.subheader("Améliorations :construction:")
st.caption("Algo :computer:" )
st.write("Il y a certainement la possibilité d'aller plus vite qu'actuellement en explorant les options qu'offre l'OSRM (le traitement total prend 9h actuellement avec une instance OSRM sur une machine en local).")
st.write("Les géométries des parcs sont récupérées sous forme de polygones puis résumées sous forme de centroïdes, ce qui pose des problèmes de représentativité pour des parcs de grand taille comme Pech-David.")
st.caption("Data-visualisation :chart:"	)
st.write("Côté dataviz il serait sympa de pouvoir cliquer sur un carreau et que le parc correspondant pop (par un highlight ou autre) mais pour l'instant je n'ai pas réussi à trouver la solution avec folium.")
st.write("L'idéal serait de passer sous Mapbox.js, qui offre une plus grande accessibilité, de créer une interface dédiée, de servir les géométries avec une API........")
st.write("Quitte à refaire le calcul, on pourrait garder le nom des parcs.")

st.subheader("Sources")
st.caption("Les données :white_check_mark:" )
st.write("Filosofi (Fichier Localisé Social et Fiscal), carreaux 200m | INSEE - 2015")
st.write("Parcs OSM | API Overpass - utilisée le 22/07/2023")
st.write("Réseau viaire OSM | GEOFABRIK - màj le 24/07/2023")
st.caption("Le code :cat2:")
st.write("[Le repo pour les calculs est ici](https://github.com/Lecaethomas/walkAndPark_backend/tree/master)")
st.write("[Le repo pour la dataviz est ici](https://github.com/Lecaethomas/walkAndPark_backend/tree/master)")


