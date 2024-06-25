import requests
import geopandas as gpd
import os

def fetch_county_geometry(output_folder):
    # Define the URL for the ArcGIS REST service
    url = ("https://maps.nj.gov/arcgis/rest/services/Framework/Government_Boundaries/MapServer/1/query"
           "?where=GNIS_NAME+%3D+%27County+of+Atlantic%27&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps"
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
        print("No features found for the specified query.")
        print("Response data:", data)
        return

    # Convert the features to a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(data['features'])

    # Set the geometry column if it exists
    if 'geometry' in gdf:
        gdf.set_geometry('geometry', inplace=True)

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define the output file path
    output_filename = "County_of_Atlantic_boundary.shp"
    output_path = os.path.join(output_folder, output_filename)

    # Save the GeoDataFrame as a shapefile
    gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"Data saved successfully to {output_path}")

# Example usage
output_folder = "C:/Users/tug37130/Documents/CED/Output_Testing"
fetch_county_geometry(output_folder)
