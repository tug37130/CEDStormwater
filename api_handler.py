import requests
import json

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

def fetch_roads(url, municipality_boundary):
    query = {
        'geometry': json.dumps(municipality_boundary),
        'geometryType': 'esriGeometryPolygon',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',
        'outSR': 4326,
        'f': 'json'
    }
    response = requests.get(url + '/query', params=query)
    response.raise_for_status()
    return response.json()

def fetch_wetlands(url, municipality_boundary):
    query = {
        'geometry': json.dumps(municipality_boundary),
        'geometryType': 'esriGeometryPolygon',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',
        'outSR': 4326,
        'f': 'json'
    }
    response = requests.get(url + '/query', params=query)
    response.raise_for_status()
    return response.json()