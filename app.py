import os
import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import folium_static

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the result GeoDataFrame from the shapefile
result_shapefile_path = os.path.join(current_dir, "data", "grid_walk_results_.shp")  # Change the file name to your polygons shapefile
result_gdf = gpd.read_file(result_shapefile_path)

# Load the park GeoDataFrame from the shapefile
park_shapefile_path = os.path.join(current_dir, "data", "public_parks.shp")
park_gdf = gpd.read_file(park_shapefile_path)

# Create a folium map centered at the centroid of the first polygon in result_gdf
m = folium.Map(location=[result_gdf["geometry"].centroid.y.mean(), result_gdf["geometry"].centroid.x.mean()], zoom_start=12)

# Create a colormap for the walking times (gradient of reds)
min_walking_time = result_gdf["walking_ti"].min()
max_walking_time = result_gdf["walking_ti"].max()
color_scale = folium.LinearColormap(colors=['#ffffd4', '#fed98e', '#fe9929', '#d95f0e', '#993404'], vmin=min_walking_time, vmax=max_walking_time)

# Add the polygons with walking times to the map using GeoJson
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
        tooltip=f"Temps à pieds {walking_time} secondes  <br> Identifiant du parc correspondant : {park_cor}",  # Add tooltip for the polygons
    ).add_to(m)

# Add park polygons to the map
for idx, row in park_gdf.iterrows():
    park_id = row["id"]
    park_polygon = row.geometry
    folium.GeoJson(
        park_polygon.__geo_interface__,
        style_function=lambda x: {"fillColor": "transparent", "color": "blue", "weight": 2},
        tooltip=f"Identifiant du parc: {park_id}",  # Add tooltip for the parks
        name=f"Park {park_id}",
    ).add_to(m)

# Add the colormap to the map
color_scale.caption = "Temps à pieds (secondes)"
color_scale.add_to(m)


############ TEXT
# Add a title to the app
st.title("Analyse de l'accessibilité des parcs urbains toulousains")
st.subheader("Quoi? :deciduous_tree:" )
# Add some normal text describing the map
st.write("Cette carte montre l'accessibilité à des parcs calculée pour des personnes valides depuis le centre des carrés. Ces derniers font 200m*200m et correspondent à la base de données Filosofi de l'INSEE, laquelle permet de connaître les revenus moyens des ménages à l'échelle de cette unité qu'est le carreau (ce qui laisse entrevoir des analyses intéressantes). Ce carroyage se base sur les revenus fiscaux des foyers et ne recense de carreau que là où des foyers existent d'une part et que l'on peut garantir leur anonymat d'autre part")
st.write("Les temps de déplacements sont représentés en utilisant une échelle de couleurs allant du jaune au marron, la première correspondant à un temps cours, la deuxième à un temps long")

# Display the folium map in the Streamlit app using streamlit_folium's folium_static function
folium_static(m)
st.subheader("Comment? :question:" )
st.write("Techniquement le principe derrière cette modélisation est que l'on récupère le centroïde de chaque carreau, pour ensuite faire appel à l'API overpass (données OSM) permettant de récupérer les polygones correspondant aux parcs (leisure = parks) dans un rayon de 1km.")
st.write("L'algorithme fait ensuite appel à l'OSRM (Open Source Routing Machine) pour chaque point et chaque parc correspondant pour calculer le temps nécessaire pour le rejoindre à pieds (modalité 'Route'). On peut ensuite extraire le parc le plus proche ainsi que le temps nécessaire pour s'y rendre.")
st.subheader("Améliorations :construction:")
st.caption("Algo :computer:" )
st.write("En travaillant avec l'OSRM j'ai découvert qu'il était possible de calculer le plus proche élément (modalité 'Nearest') entre un point de départ et un set de points d'arrivée, ce qui permettrait de trouver directement le chemin le plus court")
st.caption("Data-visualisation :chart:"	)
st.write("Côté dataviz il serait sympa de pouvoir cliquer sur un carreau et que le parc correspondant pop (par un highlight ou autre) mais pour l'instant je n'ai pas réussi à trouver la solution.")
st.write("Quitte à refaire le calcul, on pourrait garder le nom des parcs...")
st.caption("Le code :cat2:")
st.write("[Le repo pour les calculs est ici](https://github.com/Lecaethomas/walkAndPark_backend/tree/master)")
st.write("[Le repo pour la dataviz est ici](https://github.com/Lecaethomas/walkAndPark_backend/tree/master)")


