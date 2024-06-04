from arcgis.gis import GIS
import pandas as pd

def create_arcgis_group():
    gis = GIS("home")
    group = gis.groups.create(title="Geo Processing Group", tags="geojson, shapefile")
    return group

def add_users(group, excel_file):
    df = pd.read_excel(excel_file)
    users = df['Usernames'].tolist()
    for user in users:
        group.add_users([user])

def upload_shapefiles(group, shapefiles):
    for shp in shapefiles:
        group.add_items([shp])
