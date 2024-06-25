from arcgis.gis import GIS
import pandas as pd

def create_arcgis_group(username, password, group_name):
    # Log in to ArcGIS Online
    gis = GIS("https://temple.maps.arcgis.com", username, password)

    # Create a new group
    group_properties = {
        'title': group_name,
        'tags': 'geojson, shapefile',
        'description': 'Group for GeoJSON and shapefile uploads',
        'access': 'private'
    }
    group = gis.groups.create(group_properties)
    return group

def add_users(group, excel_file):
    df = pd.read_excel(excel_file)
    users = df['Usernames'].tolist()
    for user in users:
        group.add_users([user])

def upload_shapefiles(group, shapefiles):
    for shp in shapefiles:
        group.add_items([shp])
