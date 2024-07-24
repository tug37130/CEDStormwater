import requests
import json
import logging
import geopandas as gpd
import urllib.parse
import pandas as pd
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Fetch county boundary data
def fetch_county_boundary(county_name, output_folder, project_number):
    # Construct the URL for the API request using the county_name variable.
    url = (f"https://maps.nj.gov/arcgis/rest/services/Framework/Government_Boundaries/MapServer/1/query"
           f"?where=GNIS_NAME+%3D+%27County+of+{county_name}%27&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps"
           "&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot"
           "&relationParam=&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR="
           "&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics="
           "&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount="
           "&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters="
           "&featureEncoding=esriDefault&f=geojson")

    # Send the request
    response = requests.get(url, verify=False)
    response.raise_for_status()  # Raise an error if the request failed
    data = response.json()

    # Check if features were returned
    if not data['features']:
        print("No features found for the specified query.")
        print("Response data:", data)
        return

    # Convert the response data to a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(data['features'])

    # Set the geometry column if it exists
    if 'geometry' in gdf:
        gdf.set_geometry('geometry', inplace=True)

    # Set the coordinate reference system to 4326
    gdf.set_crs("EPSG:4326", inplace=True)

    # Create the output (sub)folder if it doesn't exist
    output_folder = os.path.join(output_folder, f"County_Boundary_{project_number}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define the output filename and save the GeoDataFrame as a shapefile
    output_filename = f"County_of_{county_name}_Boundary_{project_number}.shp"
    output_path = os.path.join(output_folder, output_filename)
    gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {output_path}")
    return output_path

# Fetch parcels data
def fetch_parcels(municipality_code, output_folder, project_number):
    url = "https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Hosted_Parcels_Test_WebMer_20201016/FeatureServer/0"
    where_clause = f"PCL_MUN='{municipality_code}'"
    fields = "*"

    # Initial request to get max record count
    urlstring = url + "?f=json"
    response = requests.get(urlstring)
    response.raise_for_status()
    data = response.json()
    max_record_count = int(data["maxRecordCount"])

    # Request to get all object IDs
    encoded_where_clause = urllib.parse.quote(where_clause)
    urlstring = f"{url}/query?where={encoded_where_clause}&returnIdsOnly=true&f=json"
    response = requests.get(urlstring)
    response.raise_for_status()
    data = response.json()
    id_field = data["objectIdFieldName"]
    id_list = data["objectIds"]
    id_list.sort()
    num_records = len(id_list)

    # Fetch features in chunks based on max record count (workaround to 2000 item request limit)
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

    # Concatenate all GeoDataFrames and set CRS
    final_gdf = pd.concat(feature_list, ignore_index=True)
    final_gdf.set_crs("EPSG:4326", inplace=True)

    # Create the output (sub)folder if it doesn't exist
    output_folder = os.path.join(output_folder, f"Parcels_{project_number}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define the output filename and save the GeoDataFrame as a shapefile
    output_filename = f"Parcels_{project_number}.shp"
    output_path = os.path.join(output_folder, output_filename)
    final_gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {output_path}")
    return output_path

# Fetch roads
def fetch_roads(gnis_code, output_folder, project_number):
    url = "https://maps.nj.gov/arcgis/rest/services/Framework/Transportation/MapServer/14"
    where_clause = f"COUNTY_L='{gnis_code}'"
    fields = "*"
    urlstring = url + "?f=json"
    response = requests.get(urlstring)
    data = response.json()
    max_record_count = int(data["maxRecordCount"])

    # Request to get all object IDs
    encoded_where_clause = urllib.parse.quote(where_clause)
    urlstring = f"{url}/query?where={encoded_where_clause}&returnIdsOnly=true&f=json"
    response = requests.get(urlstring)
    data = response.json()
    id_field = data["objectIdFieldName"]
    id_list = data["objectIds"]
    id_list.sort()
    num_records = len(id_list)

    # Fetch features in chunks based on max record count (workaround to 2000 item request limit)
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

    # Concatenate all GeoDataFrames and set CRS
    final_gdf = pd.concat(feature_list, ignore_index=True)
    final_gdf.set_crs("EPSG:4326", inplace=True)

    # Create the output (sub)folder if it doesn't exist
    output_folder = os.path.join(output_folder, f"Roads_{project_number}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define the output filename and save the GeoDataFrame as a shapefile
    output_filename = f"Roads_{project_number}.shp"
    output_path = os.path.join(output_folder, output_filename)
    final_gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {output_path}")
    return output_path

# Fetch municipality boundary data
def fetch_municipality_boundary(municipality_code, output_folder, municipality_name, project_number):
    url = (f"https://maps.nj.gov/arcgis/rest/services/Framework/Government_Boundaries/MapServer/2/query"
           f"?where=MUN_CODE+%3D+%27{municipality_code}%27&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps"
           "&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot"
           "&relationParam=&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR="
           "&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics="
           "&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount="
           "&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters="
           "&featureEncoding=esriDefault&f=geojson")

    # Send the API request
    response = requests.get(url, verify=False)
    response.raise_for_status()  # Raise an error if the request failed
    data = response.json()

    # Check if features were returned
    if not data['features']:
        print("No features found for the specified query.")
        print("Response data:", data)
        return

    # Convert the response data to a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(data['features'])

    # Set the geometry column if it exists
    if 'geometry' in gdf:
        gdf.set_geometry('geometry', inplace=True)

    # Set the coordinate reference system to 4326
    gdf.set_crs("EPSG:4326", inplace=True)

    # Create the output (sub)folder if it doesn't exist
    output_folder = os.path.join(output_folder, f"Municipality_Boundary_{project_number}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define the output filename and save the GeoDataFrame as a shapefile
    sanitized_municipality_name = municipality_name.replace(" ", "_")
    output_filename = f"{sanitized_municipality_name}_Boundary_{project_number}.shp"
    output_path = os.path.join(output_folder, output_filename)
    gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {output_path}")
    return output_path

# Fetch wetlands data within municipal_boundary bounding box
def fetch_wetlands_within_boundary(boundary_gdf, output_folder, project_number):
    url = "https://mapsdep.nj.gov/arcgis/rest/services/Features/Land_lu/MapServer/2/query"

    # Define the bounding box for the query
    bounds = boundary_gdf.total_bounds
    bbox = {
        "xmin": bounds[0],
        "ymin": bounds[1],
        "xmax": bounds[2],
        "ymax": bounds[3],
        "spatialReference": {"wkid": 4326}
    }

    # Define the parameters for the API request
    params = {
        "where": "1=1",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "geometry": json.dumps(bbox),
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson"
    }

    # Send the API request
    response = requests.post(url, data=params, verify=False)
    response.raise_for_status()  # Raise an error if the request failed
    data = response.json()

    # Check if features were returned
    if not data['features']:
        print("No features found for the specified query.")
        print("Response data:", data)
        return None

    # Convert the response data to a GeoDataFrame
    wetlands_gdf = gpd.GeoDataFrame.from_features(data['features'])
    wetlands_gdf.set_crs("EPSG:4326", inplace=True)

    # Create the output (sub)folder if it doesn't exist
    wetlands_output_folder = os.path.join(output_folder, f"Wetlands_{project_number}")
    if not os.path.exists(wetlands_output_folder):
        os.makedirs(wetlands_output_folder)

    # Define the output filename and save the GeoDataFrame as a shapefile
    wetlands_output_filename = f"Wetlands_{project_number}.shp"
    wetlands_output_path = os.path.join(wetlands_output_folder, wetlands_output_filename)
    wetlands_gdf.to_file(wetlands_output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {wetlands_output_path}")
    return wetlands_output_path

# Fetch neighboring municipalities data using municipal_boundary bounding box
def fetch_neighboring_municipalities(boundary_gdf, output_folder, project_number):
    url = "https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/NJ_Municipal_Boundaries_3424/FeatureServer/0/query"

    # Define the bounding box for the query
    bounds = boundary_gdf.total_bounds
    bbox = {
        "xmin": bounds[0],
        "ymin": bounds[1],
        "xmax": bounds[2],
        "ymax": bounds[3],
        "spatialReference": {"wkid": 4326}
    }

    # Define the parameters for the API request
    params = {
        "where": "1=1",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "geometry": json.dumps(bbox),
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson"
    }

    # Send the API request
    response = requests.post(url, data=params, verify=False)
    response.raise_for_status()  # Raise an error if the request failed
    data = response.json()

    # Check if features were returned
    if not data['features']:
        print("No features found for the specified query.")
        print("Response data:", data)
        return None

    # Convert the response data to a GeoDataFrame
    neighboring_gdf = gpd.GeoDataFrame.from_features(data['features'])
    neighboring_gdf.set_crs("EPSG:4326", inplace=True)

    # Create the output (sub)folder if it doesn't exist
    neighboring_output_folder = os.path.join(output_folder, f"Neighboring_Municipalities_{project_number}")
    if not os.path.exists(neighboring_output_folder):
        os.makedirs(neighboring_output_folder)

    # Define the output filename and save the GeoDataFrame as a shapefile
    neighboring_output_filename = f"Neighboring_Municipalities_{project_number}.shp"
    neighboring_output_path = os.path.join(neighboring_output_folder, neighboring_output_filename)
    neighboring_gdf.to_file(neighboring_output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {neighboring_output_path}")
    return neighboring_output_path

# Fetch waterbodies data within the municipal_boundary bounding box
def fetch_waterbodies_within_boundary(boundary_gdf, output_folder, project_number):
    url = "https://mapsdep.nj.gov/arcgis/rest/services/Features/Hydrography/MapServer/33/query"

    # Define the bounding box for the query
    bounds = boundary_gdf.total_bounds
    bbox = {
        "xmin": bounds[0],
        "ymin": bounds[1],
        "xmax": bounds[2],
        "ymax": bounds[3],
        "spatialReference": {"wkid": 4326}
    }

    # Define the parameters for the API request
    params = {
        "where": "1=1",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "geometry": json.dumps(bbox),
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson"
    }

    # Send the API request
    response = requests.post(url, data=params, verify=False)
    response.raise_for_status()  # Raise an error if the request failed
    data = response.json()

    # Check if features were returned
    if not data['features']:
        print("No features found for the specified query.")
        print("Response data:", data)
        return None

    # Convert the response data to a GeoDataFrame
    waterbodies_gdf = gpd.GeoDataFrame.from_features(data['features'])
    waterbodies_gdf.set_crs("EPSG:4326", inplace=True)

    # Create the output (sub)folder if it doesn't exist
    waterbodies_output_folder = os.path.join(output_folder, f"Waterbodies_{project_number}")
    if not os.path.exists(waterbodies_output_folder):
        os.makedirs(waterbodies_output_folder)

    # Define the output filename and save the GeoDataFrame as a shapefile
    waterbodies_output_filename = f"Waterbodies_{project_number}.shp"
    waterbodies_output_path = os.path.join(output_folder, waterbodies_output_filename)
    waterbodies_gdf.to_file(waterbodies_output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {waterbodies_output_path}")
    return waterbodies_output_path
