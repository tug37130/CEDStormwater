import geopandas as gpd

def save_shapefile(gdf, output_folder):
    filename = f"{output_folder}/clipped_data_{gdf.crs.to_epsg()}.shp"
    gdf.to_file(filename)
    return filename
