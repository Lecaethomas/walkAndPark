import os
import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import folium_static

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the result GeoDataFrame from the shapefile
result_shapefile_path = os.path.join(current_dir, "data", "points_walk_results_.shp")
result_gdf = gpd.read_file(result_shapefile_path)

# Load the park GeoDataFrame from the shapefile
park_shapefile_path = os.path.join(current_dir, "data", "public_parks.shp")
park_gdf = gpd.read_file(park_shapefile_path)

# Create a folium map centered at the mean of the result points
m = folium.Map(location=[result_gdf["geometry"].centroid.y.mean(), result_gdf["geometry"].centroid.x.mean()], zoom_start=12)

# Create a colormap for the walking times (gradient of reds)
min_walking_time = result_gdf["walking_ti"].min()
max_walking_time = result_gdf["walking_ti"].max()
color_scale = folium.LinearColormap(colors=["green", "yellow", "red"], vmin=min_walking_time, vmax=max_walking_time)


# Add the points with walking times to the map
for idx, row in result_gdf.iterrows():
    point = row.geometry
    walking_time = row["walking_ti"]
    folium.CircleMarker(
        location=[point.y, point.x],
        radius=6,
        popup=f"Walking Time: {walking_time} seconds",
        fill=True,
        fill_color=color_scale(walking_time),
        color=color_scale(walking_time),
        fill_opacity=0.7,
    ).add_to(m)

# Add park polygons to the map
for idx, row in park_gdf.iterrows():
    park_id = row["id"]
    park_polygon = row.geometry.__geo_interface__
    folium.GeoJson(
        park_polygon,
        style_function=lambda x: {"fillColor": "transparent", "color": "blue", "weight": 2},
        tooltip=f"Park ID: {park_id}",
        name=f"Park {park_id}",
    ).add_to(m)

# Add the colormap to the map
color_scale.caption = "Walking Time (seconds)"
color_scale.add_to(m)

# Display the folium map in the Streamlit app using streamlit_folium's folium_static function
folium_static(m)