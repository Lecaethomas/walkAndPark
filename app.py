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
color_scale = folium.LinearColormap(colors=["green", "yellow", "red"], vmin=min_walking_time, vmax=max_walking_time)

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
        tooltip=f"Walking Time: {walking_time} seconds  <br> ID du parc correspondant : {park_cor}",  # Add tooltip for the polygons
    ).add_to(m)

# Add park polygons to the map
for idx, row in park_gdf.iterrows():
    park_id = row["id"]
    park_polygon = row.geometry
    folium.GeoJson(
        park_polygon.__geo_interface__,
        style_function=lambda x: {"fillColor": "transparent", "color": "blue", "weight": 2},
        tooltip=f"Park ID: {park_id}",  # Add tooltip for the parks
        name=f"Park {park_id}",
    ).add_to(m)

# Add the colormap to the map
color_scale.caption = "Walking Time (seconds)"
color_scale.add_to(m)

# Display the folium map in the Streamlit app using streamlit_folium's folium_static function
folium_static(m)
