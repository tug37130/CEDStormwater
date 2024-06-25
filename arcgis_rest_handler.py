## Current working version:
## Loops through and makes requests based on the where_clause variable.

import urllib.request
import urllib.parse
import json
import requests
import geopandas as gpd
import pandas as pd
import os

# Set the base URL for the ArcGIS REST service
base_url = "https://maps.nj.gov/arcgis/rest/services/Framework/Transportation/MapServer/14"
fields = "*"

# Fetch the maximum record count limit from the server
urlstring = base_url + "?f=json"
response = urllib.request.urlopen(urlstring)
data = json.load(response)
max_record_count = int(data["maxRecordCount"])
print(f"Record extract limit: {max_record_count}")

# Fetch the object IDs of the features
where_clause = "COUNTY_L='882270'"
encoded_where_clause = urllib.parse.quote(where_clause)
urlstring = f"{base_url}/query?where={encoded_where_clause}&returnIdsOnly=true&f=json"
response = urllib.request.urlopen(urlstring)
data = json.load(response)
id_field = data["objectIdFieldName"]
id_list = data["objectIds"]
id_list.sort()
num_records = len(id_list)
print(f"Number of target records: {num_records}")

# Gather features
print("Gathering records...")
feature_list = []
for i in range(0, num_records, max_record_count):
    to_record = i + (max_record_count - 1)
    if to_record > num_records:
        to_record = num_records - 1
    from_id = id_list[i]
    to_id = id_list[to_record]
    where = f"{id_field}>={from_id} AND {id_field}<={to_id} AND {where_clause}"
    encoded_where = urllib.parse.quote(where)
    urlstring = f"{base_url}/query?where={encoded_where}&returnGeometry=true&outFields={fields}&f=geojson"
    response = requests.get(urlstring, verify=False)
    data = response.json()
    gdf = gpd.GeoDataFrame.from_features(data['features'])
    # Merge data
    feature_list.append(gdf)

# Concatenate all parts into a single GeoDataFrame
final_gdf = pd.concat(feature_list, ignore_index=True)
output_folder = 'C:/Users/tug37130/Documents/CED/Output_Testing'
output_filename = 'monmouth_roads.shp'
output_path = os.path.join(output_folder, output_filename)
final_gdf.to_file(driver='ESRI Shapefile', filename=output_path)
print(f"Data saved successfully to {output_path}")
