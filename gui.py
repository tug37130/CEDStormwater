import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
from api_handler import (
    fetch_municipal_boundary, fetch_parcels,
    fetch_roads
)
from geo_processor import create_geodataframe, save_shapefile, clip_to_boundary
from arcgis_online import create_arcgis_group, add_users, upload_shapefiles
from logger import log_operations
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)

def launch_gui():
    root = tk.Tk()
    root.title("Geo Processing Application")

    def select_output_folder():
        folder_selected = filedialog.askdirectory()
        output_folder.set(folder_selected)

    tk.Label(root, text="Municipality Code").grid(row=0, column=0)
    municipality_code = tk.Entry(root, width=50)
    municipality_code.grid(row=0, column=1)

    tk.Label(root, text="County Name").grid(row=1, column=0)
    county_name = tk.Entry(root, width=50)
    county_name.grid(row=1, column=1)

    tk.Label(root, text="Output Folder").grid(row=2, column=0)
    output_folder = tk.StringVar()
    tk.Entry(root, textvariable=output_folder, width=50).grid(row=2, column=1)
    tk.Button(root, text="Browse", command=select_output_folder).grid(row=2, column=2)

    tk.Button(root, text="Run", command=lambda: run_process(municipality_code.get(), county_name.get(), output_folder.get())).grid(row=3, column=1)

    root.mainloop()

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def run_process(municipality_code, county_name, output_folder):
    try:
        username = simpledialog.askstring("Input", "Enter your ArcGIS Online username:")
        password = simpledialog.askstring("Input", "Enter your ArcGIS Online password:", show='*')
        group_name = simpledialog.askstring("Input", "Enter the name for the new ArcGIS Online group:")

        session = requests_retry_session()

        logging.info("Fetching municipal boundary...")
        municipal_boundary = fetch_municipal_boundary(municipality_code)
        logging.info(f"Municipal boundary fetched successfully: {municipal_boundary}")

        logging.info("Fetching parcels data...")
        parcels_data = fetch_parcels(municipality_code)
        logging.info(f"Parcels data fetched successfully: {parcels_data}")

        logging.info("Fetching roads data...")
        roads_data = fetch_roads("https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Tran_road/FeatureServer/0")
        logging.info(f"Roads data fetched successfully: {roads_data}")

        logging.info("Converting municipal boundary to GeoDataFrame...")
        municipal_boundary_gdf = create_geodataframe(municipal_boundary['features'])
        logging.info("Municipal boundary GeoDataFrame created successfully")

        logging.info("Converting roads data to GeoDataFrame...")
        roads_gdf = create_geodataframe(roads_data['features'])
        logging.info("Roads GeoDataFrame created successfully")

        logging.info("Clipping roads data to municipal boundary...")
        clipped_roads_gdf = clip_to_boundary(roads_gdf, municipal_boundary_gdf)
        logging.info("Clipped roads GeoDataFrame created successfully")

        logging.info("Fetched all data successfully")

        # Check for None or empty features
        if not parcels_data.get('features'):
            raise ValueError("No features found in parcels data")

        if clipped_roads_gdf.empty:
            raise ValueError("No features found in clipped roads data")

        logging.info("Creating GeoDataFrame for parcels...")
        parcels_gdf = create_geodataframe(parcels_data['features'])
        logging.info("GeoDataFrame for parcels created successfully")

        logging.info("Saving parcels shapefile...")
        parcels_shapefile = save_shapefile(parcels_gdf, output_folder, "parcels")
        logging.info("Parcels shapefile saved successfully")

        logging.info("Saving clipped roads shapefile...")
        roads_shapefile = save_shapefile(clipped_roads_gdf, output_folder, "roads")
        logging.info("Clipped roads shapefile saved successfully")

        logging.info("All shapefiles saved successfully")

        logging.info("Creating ArcGIS group...")
        group = create_arcgis_group(username, password, group_name)
        logging.info("ArcGIS group created successfully")

        logging.info("Adding users to group...")
        add_users(group, "users.xlsx")
        logging.info("Users added to group successfully")

        logging.info("Uploading shapefiles to ArcGIS Online...")
        upload_shapefiles(group, [parcels_shapefile, roads_shapefile])
        logging.info("Shapefiles uploaded to ArcGIS Online successfully")

        log_operations(municipality_code, output_folder, group.title)
        logging.info("Process completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    launch_gui()
