import requests
import json
import logging
import urllib.parse
import geopandas as gpd
import pandas as pd

logging.basicConfig(level=logging.INFO)

def fetch_municipal_boundary(municipality_code):
    url = f"https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/NJ_Municipalities_3857/FeatureServer/0/query?where=MUN_CODE%20%3D%20'{municipality_code}'&outFields=*&outSR=4326&f=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_parcels(municipality_code):
    url = f"https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/arcgis/rest/services/Hosted_Parcels_Test_WebMer_20201016/FeatureServer/0/query?where=PCL_MUN%20%3D%20'{municipality_code}'&outFields=*&outSR=4326&f=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_roads(url, where_clause):
    fields = "*"
    # Fetch the maximum record count limit from the server
    urlstring = url + "?f=json"
    response = requests.get(urlstring)
    data = response.json()
    max_record_count = int(data["maxRecordCount"])

    # Fetch the object IDs of the features
    encoded_where_clause = urllib.parse.quote(where_clause)
    urlstring = f"{url}/query?where={encoded_where_clause}&returnIdsOnly=true&f=json"
    response = requests.get(urlstring)
    data = response.json()
    id_field = data["objectIdFieldName"]
    id_list = data["objectIds"]
    id_list.sort()
    num_records = len(id_list)

    # Gather features
    feature_list = []
    for i in range(0, num_records, max_record_count):
        to_record = i + (max_record_count - 1)
        if to_record > num_records:
            to_record = num_records - 1
        from_id = id_list[i]
        to_id = id_list[to_record]
        where = f"{id_field}>={from_id} AND {id_field}<={to_id} AND {where_clause}"
        encoded_where = urllib.parse.quote(where)
        urlstring = f"{url}/query?where={encoded_where}&returnGeometry=true&outFields={fields}&f=geojson"
        response = requests.get(urlstring)
        data = response.json()
        gdf = gpd.GeoDataFrame.from_features(data['features'])
        feature_list.append(gdf)

    # Concatenate all parts into a single GeoDataFrame
    final_gdf = pd.concat(feature_list, ignore_index=True)
    return final_gdf
