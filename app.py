import os
import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import folium_static
import folium.plugins as plugins
from folium import DivIcon


## define few functions
def convert_seconds_to_minutes_seconds(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes} minutes {remaining_seconds} secondes"

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the result GeoDataFrame from the shapefile
result_shapefile_path = os.path.join(current_dir, "data", "grid_walk_results.geojson") 
result_gdf = gpd.read_file(result_shapefile_path) 

# Load the park GeoDataFrame from the shapefile
park_shapefile_path = os.path.join(current_dir, "data", "public_parks.geojson")
park_gdf = gpd.read_file(park_shapefile_path)
# Load the "toulouse.geojson" file
contours_shapefile_path = os.path.join(current_dir, "data", "toulouse.geojson")
toulouse_gdf = gpd.read_file(contours_shapefile_path)

# Create a folium map centered on Toulouse
m = folium.Map(location=[43.6, 1.43], zoom_start=12, tiles=None, control_scale = True) # Aucune basemap à l'origine pour pouvoir ajouter OSM avec les attributions que j'aurais choisies
folium.raster_layers.TileLayer(tiles='openstreetmap', name='OpenStreetMap').add_to(m)


## Satellite Basemap
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='ESRI Satellite',
    name='ESRI Satellite'
).add_to(m)

##### City contours
# Add toulouse polygon to the map
for idx, row in toulouse_gdf.iterrows():
    toulouse_polygon = row.geometry
    folium.GeoJson(
        toulouse_polygon,
        style_function=lambda x: {"fillColor": "transparent", "color": "black", "weight": 3},
        name="Commune de Toulouse",
    ).add_to(m) 
 
# Create another folium layer for the walking times 
walk_times_layer = folium.FeatureGroup(name="Carroyage - temps à pieds pour accéder au parc le plus proche")

## add geocoder in case the user searches for his streets 
plugins.Geocoder(
    collapsed = False,
    position = 'bottomright',
    add_marker = True).add_to(m) 
 
# Create a colormap for the walking times (gradient of reds)
min_walking_time = result_gdf["walking_ti"].min()
max_walking_time = result_gdf["walking_ti"].max()
color_scale = folium.LinearColormap(colors=['#ffffd4', '#fed98e', '#fe9929', '#d95f0e', '#993404'], vmin=round(min_walking_time), vmax=round(max_walking_time))

#### GRID

# Add the polygons with walking times to the walk_times_layer
for idx, row in result_gdf.iterrows():
    polygon = row.geometry
    walking_time = row["walking_ti"]
    park_cor = row["park_id"]
    men_coll = row["Men_coll"]
    men_pauv = row["Men_pauv"]
    men = row["Men"]
    z_index = int(1000 - walking_time) if walking_time >= 0 else 0

    # popup_content = f"Temps à pieds {round(walking_time)} secondes<br>Identifiant du parc correspondant: {park_cor}<br>Nombre de ménages en logement collectif: {round(men_coll)}"
    folium.GeoJson(
        polygon.__geo_interface__,
        overlay=True,  # Ensure each GeoJson feature is a separate overlay
        highlight_function= lambda feat: {'fillColor': 'yellow'},
        smooth_factor=0,  # Disable smoothing to prevent artifacts

        style_function=lambda x, walking_time=walking_time: {
            "fillColor": color_scale(walking_time),
            "color": color_scale(walking_time),
            "weight": 2,
            "fillOpacity": 0.7,
        },
        tooltip=f"<strong>Temps à pieds pour accéder au parc le plus proche en 2023:</strong> {convert_seconds_to_minutes_seconds(round(walking_time))}<br><strong>Identifiant du parc correspondant:</strong> {park_cor}<br><br><strong>| Informations statistiques pour l'année 2015 | </strong></br><strong>Nombre de ménages en logement collectif:</strong> {round(men_coll)} <br><strong>Nombre de ménages pauvres: </strong> {round(men_pauv)}<br><strong> Nombre total de ménages: </strong> {round(men)}</br>",
        # popup=folium.Popup(html=popup_content, max_width=200),  # Adding the popup 
  
    ).add_to(walk_times_layer)  

##### PARCS
# Create a folium layer for the parks
parks_layer = folium.FeatureGroup(name="Parcs", show = False) 

# Add park points to the parks_layer
for idx, row in park_gdf.iterrows():
    park_id = row["id"]
    park_point = row.geometry  # Assuming the geometry represents a single point
    # Customize the styling options here
    park_style = {
        "radius": 5,  
        "color": "Green", 
        "fill_color": "Green", 
        "fill_opacity": 0.2,
    }
    folium.CircleMarker(
        location=[park_point.y, park_point.x],   
        radius=park_style["radius"],
        color=park_style["color"],
        fill_color=park_style["fill_color"],
        fill_opacity=park_style["fill_opacity"], 
        tooltip=f"Identifiant du parc: {park_id}",
        popup=f"ID : {park_id}",
    ).add_to(parks_layer)

# Add the parks_layer and walk_times_layer to the map
walk_times_layer.add_to(m)
parks_layer.add_to(m)
plugins.Fullscreen(force_separate_button = True).add_to(m)
# Add the colormap to the map

color_scale.caption = "Temps à pieds pour accéder au parc le plus proche (secondes)"
color_scale.add_to(m)

# Add the layer control to the map
folium.LayerControl(position = 'topleft').add_to(m)

############ TEXT
# Add a title to the app
st.title("Tentative de modélisation de l'accessibilité des parcs urbains toulousains")
st.subheader("De quoi parle-t-on? :deciduous_tree:" )

# Add some normal text describing the map
st.write("Cette carte montre l'accessibilité à des parcs calculée pour des personnes non-PMR depuis le centre des carrés vers les points représentant les parcs. Les carreaux font 200m*200m et correspondent à la base de données Filosofi de l'INSEE filtrée sur la commune de Toulouse. Cette base de données fournit différents indicateurs socio-économiques à l'échelle de cette unité qu'est le carreau. Un carreau signifie la présence de ménages mais suffisamment nombreux pour garantir leur anonymat.")
st.write("Les temps de déplacements sont représentés en utilisant une échelle de couleurs allant du jaune au marron, la première correspondant à un temps cours, la deuxième à un temps long.")

# Display the folium map in the Streamlit, app using streamlit_folium's folium_static function
folium_static(m)

## Definitions 
with st.expander("Voir les définitions"):
    st.write("* Un ménage, au sens du recensement de la population, désigne l'ensemble des personnes qui partagent la même résidence principale, sans que ces personnes soient nécessairement unies par des liens de parenté. Un ménage peut être constitué d'une seule personne.")
    st.write("* Un individu (ou un ménage) est considéré comme pauvre lorsqu'il vit dans un ménage dont le niveau de vie est inférieur au seuil de pauvreté. En France le seuil est fixé à 60 % du niveau de vie médian.")

st.write("Au delà de la question de l'accessibilité à la ressource spécifique que sont les espaces verts, ce type d'analyse peut être conduit pour tous types de données (Base Permanente des Equipements, BD Topo ...) et permettre ainsi d'avoir un aperçut de la dotation des territoires en équipements ainsi que leur accessibilité et pourquoi pas d'aborder le [concept de la ville du 1/4 d'heure](https://www.moreno-web.net/wordpress/wp-content/uploads/2020/12/Livre-Blanc-2-Etude-ville-quart-heure-18.12.2020.pdf).")
st.write("Enfin, un géocodeur ([basé sur OSM/NOMINATIM](https://nominatim.org/)), situé en bas à droite de l'interface, permet à un utilisateur de facilement retrouver un lieu comme son domicile (en renseignant son adresse) afin de mieux exploiter la cartographie.")

st.subheader("Comment :question:" )
st.write("Techniquement le principe derrière cette modélisation est que l'on récupère le centroïde de chaque carreau, pour ensuite faire appel à l'API overpass (données OpenStreetMap) permettant de récupérer les polygones correspondant aux parcs dans un rayon de 1km autour de chaque point.")
st.write("L'algorithme fait ensuite appel à l'OSRM (Open Source Routing Machine) pour chaque point et les parcs correspondants afin de calculer le temps nécessaire pour les rejoindre à pieds. On peut ensuite extraire le parc le plus proche (en temps de marche) ainsi que le temps nécessaire pour s'y rendre.")

st.subheader("Améliorations :construction:")
st.caption("Algo :computer:" )
st.write("- Il y a certainement la possibilité d'aller plus vite qu'actuellement en explorant les options qu'offre l'OSRM.")
st.write("- Le traitement des géométries des parcs pourrait être affiné puisqu'il récupère un seul point sur le contour. Il y aurait peut-être la possibilité de récupérer toutes les entrées et trouver la plus proche pour chaque carreau en amont du calcul d'accessibilité.")
st.caption("Data-visualisation :chart:"	)
st.write("- Côté dataviz il serait sympa de pouvoir cliquer sur un carreau et que le parc correspondant pop (par un highlight ou autre) - et réciproquement - mais pour l'instant je n'ai pas réussi à trouver la solution avec folium.")
st.write("- Quitte à refaire le calcul, on pourrait garder le nom des parcs - et les afficher au survol par le curseur.")

st.subheader("Sources :books:") 
st.caption("Les données :white_check_mark:" )
st.write("Filosofi (Fichier Localisé Social et Fiscal), carreaux 200m | INSEE - 2015")
st.write("Parcs OSM | API Overpass - utilisée le 22/07/2023") 
st.write("Réseau viaire OSM | GEOFABRIK - 24/07/2023")
st.write("Contours de la commune de Toulouse - Admin express | IGN - 2020-01-16")
st.caption("Le code :cat2:")
st.write("[Le repo pour les calculs est ici](https://github.com/Lecaethomas/walkAndPark_backend/tree/master)")
st.write("[Le repo pour la dataviz est ici](https://github.com/Lecaethomas/walkAndPark)")