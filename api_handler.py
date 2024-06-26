import requests
import json
import logging
import urllib.parse
import geopandas as gpd
import pandas as pd

logging.basicConfig(level=logging.INFO)

def fetch_county_boundary(county_name, output_folder):
    # Encode the county name to be URL-safe
    encoded_county_name = urllib.parse.quote(f"County of {county_name}")

    # Define the URL for the ArcGIS REST service
    url = (f"https://maps.nj.gov/arcgis/rest/services/Framework/Government_Boundaries/MapServer/1/query"
           f"?where=GNIS_NAME+%3D+%27{encoded_county_name}%27&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps"
           "&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot"
           "&relationParam=&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR="
           "&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics="
           "&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount="
           "&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters="
           "&featureEncoding=esriDefault&f=geojson")

    # Make the request to the API
    response = requests.get(url, verify=False)
    response.raise_for_status()
    data = response.json()

    # Check if features are returned
    if not data['features']:
        logging.error("No features found for the specified query.")
        logging.error(f"Response data: {data}")
        return None

    # Convert the features to a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(data['features'])

    # Set the geometry column if it exists
    if 'geometry' in gdf:
        gdf.set_geometry('geometry', inplace=True)

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define the output file path
    output_filename = f"County_of_{county_name}_boundary.shp"
    output_path = os.path.join(output_folder, output_filename)

    # Save the GeoDataFrame as a shapefile
    gdf.to_file(output_path, driver='ESRI Shapefile')
    logging.info(f"Data saved successfully to {output_path}")

    return output_path

def fetch_parcels(municipality_code, output_folder):
    url = "https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Hosted_Parcels_Test_WebMer_20201016/FeatureServer/0"
    fields = "*"
    
    urlstring = url + "?f=json"
    response = requests.get(urlstring)
    response.raise_for_status()
    data = response.json()
    max_record_count = int(data["maxRecordCount"])

    where_clause = f"PCL_MUN='{municipality_code}'"
    encoded_where_clause = urllib.parse.quote(where_clause)
    urlstring = f"{url}/query?where={encoded_where_clause}&returnIdsOnly=true&f=json"
    response = requests.get(urlstring)
    response.raise_for_status()
    data = response.json()
    id_field = data["objectIdFieldName"]
    id_list = data["objectIds"]
    id_list.sort()
    num_records = len(id_list)

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
        response.raise_for_status()
        data = response.json()
        gdf = gpd.GeoDataFrame.from_features(data['features'])
        feature_list.append(gdf)

    final_gdf = pd.concat(feature_list, ignore_index=True)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_filename = "parcels_boundary.shp"
    output_path = os.path.join(output_folder, output_filename)

    final_gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {output_path}")

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
