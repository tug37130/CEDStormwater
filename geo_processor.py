import geopandas as gpd
from shapely.geometry import shape
import logging

def create_geodataframe(features):
    """Convert GeoJSON features to a GeoDataFrame, handling invalid geometries"""
    geometries = []
    valid_features = []

    for feature in features:
        try:
            geom = shape(feature["geometry"])
            geometries.append(geom)
            valid_features.append(feature)
        except Exception as e:
            logging.warning(f"Invalid geometry skipped: {feature['geometry']} Error: {e}")

    if not valid_features:
        raise ValueError("No valid geometries found in the provided GeoJSON data")

    gdf = gpd.GeoDataFrame.from_features(valid_features)
    return gdf

def save_shapefile(gdf, folder_path, filename):
    """Save GeoDataFrame as a shapefile"""
    shapefile_path = f"{folder_path}/{filename}.shp"
    gdf.to_file(shapefile_path)
    return shapefile_path

def clip_to_boundary(geo_df, boundary_gdf):
    """Clip GeoDataFrame to the boundary of another GeoDataFrame"""
    return gpd.clip(geo_df, boundary_gdf)
