import requests
import json
import logging
import geopandas as gpd
import urllib.parse
import pandas as pd

logging.basicConfig(level=logging.INFO)

def fetch_county_boundary(county_name, output_folder):
    url = ("https://maps.nj.gov/arcgis/rest/services/Framework/Government_Boundaries/MapServer/1/query"
           f"?where=GNIS_NAME+%3D+%27County+of+{county_name}%27&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps"
           "&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot"
           "&relationParam=&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR="
           "&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics="
           "&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount="
           "&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters="
           "&featureEncoding=esriDefault&f=geojson")

    response = requests.get(url, verify=False)
    response.raise_for_status()
    data = response.json()

    if not data['features']:
        print("No features found for the specified query.")
        print("Response data:", data)
        return

    gdf = gpd.GeoDataFrame.from_features(data['features'])

    if 'geometry' in gdf:
        gdf.set_geometry('geometry', inplace=True)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_filename = f"County_of_{county_name}_boundary.shp"
    output_path = os.path.join(output_folder, output_filename)
    gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {output_path}")

def fetch_parcels(municipality_code, output_folder):
    url = ("https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Hosted_Parcels_Test_WebMer_20201016/FeatureServer/0/query"
           f"?where=PCL_MUN+%3D+%27{municipality_code}%27&objectIds=&time=&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects"
           "&resultType=none&distance=0.0&units=esriSRUnit_Meter&relationParam=&returnGeodetic=false&outFields=*&returnGeometry=true"
           "&returnCentroid=false&returnEnvelope=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR="
           "&defaultSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false"
           "&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics="
           "&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=geojson")

    response = requests.get(url, verify=False)
    response.raise_for_status()
    data = response.json()

    if not data['features']:
        print("No features found for the specified query.")
        print("Response data:", data)
        return

    gdf = gpd.GeoDataFrame.from_features(data['features'])

    if 'geometry' in gdf:
        gdf.set_geometry('geometry', inplace=True)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_filename = "parcels_boundary.shp"
    output_path = os.path.join(output_folder, output_filename)
    gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {output_path}")

def fetch_roads(url, where_clause):
    fields = "*"
    urlstring = url + "?f=json"
    response = requests.get(urlstring)
    data = response.json()
    max_record_count = int(data["maxRecordCount"])

    encoded_where_clause = urllib.parse.quote(where_clause)
    urlstring = f"{url}/query?where={encoded_where_clause}&returnIdsOnly=true&f=json"
    response = requests.get(urlstring)
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
        data = response.json()
        gdf = gpd.GeoDataFrame.from_features(data['features'])
        feature_list.append(gdf)

    final_gdf = pd.concat(feature_list, ignore_index=True)
    return final_gdf
