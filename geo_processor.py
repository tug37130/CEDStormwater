import geopandas as gpd
from shapely.geometry import shape

def clip_to_boundary(geojson, boundary_geojson):
    boundary_gdf = gpd.GeoDataFrame.from_features(boundary_geojson["features"])
    gdf = gpd.GeoDataFrame.from_features(geojson["features"])
    clipped_gdf = gpd.clip(gdf, boundary_gdf)
    return clipped_gdf
