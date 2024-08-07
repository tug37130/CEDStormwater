import geopandas as gpd
import os
import logging

# Ensure each file is saved as 4326.
def check_crs(shapefile, target_crs="EPSG:4326"):
    try:
        gdf = gpd.read_file(shapefile)
        return gdf.crs == target_crs
    except Exception as e:
        logging.error(f"An error occurred while checking CRS: {e}")
        return False

# Project the file if needed.
def reproject_shapefile(input_shapefile, output_shapefile, target_crs="EPSG:4326"):
    try:
        logging.info(f"Reprojecting {input_shapefile} to {target_crs}...")
        gdf = gpd.read_file(input_shapefile)
        
        if gdf.crs is None:
            logging.info(f"Setting CRS for {input_shapefile} to WGS84 (EPSG:4326)...")
            gdf.set_crs("EPSG:4326", inplace=True)
        
        gdf = gdf.to_crs(target_crs)
        gdf.to_file(output_shapefile)
        logging.info(f"Reprojected shapefile saved as {output_shapefile}")
        return output_shapefile
    except Exception as e:
        logging.error(f"An error occurred while reprojecting shapefile: {e}")
        return None

# Clip the layer if needed.
def clip_shapefile(input_shapefile, boundary_shapefile, output_shapefile):
    try:
        logging.info(f"Clipping {input_shapefile} to {boundary_shapefile}...")
        gdf = gpd.read_file(input_shapefile)
        boundary_gdf = gpd.read_file(boundary_shapefile)

        clipped_gdf = gpd.clip(gdf, boundary_gdf)
        
        output_folder = os.path.dirname(output_shapefile)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        clipped_gdf.to_file(output_shapefile)
        logging.info(f"Clipped shapefile saved as {output_shapefile}")
        return output_shapefile
    except Exception as e:
        logging.error(f"An error occurred while clipping shapefile: {e}")
        return None
