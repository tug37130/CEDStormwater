import tkinter as tk
from tkinter import filedialog
from api_handler import (
    fetch_geojson, fetch_municipal_boundary, fetch_parcels,
    fetch_roads, fetch_wetlands
)
from geo_processor import clip_to_boundary
from file_manager import save_shapefile
from arcgis_online import create_arcgis_group, add_users, upload_shapefiles
from logger import log_operations

def launch_gui():
    root = tk.Tk()
    root.title("Stormwater Project Automation")

    def select_output_folder():
        folder_selected = filedialog.askdirectory()
        output_folder.set(folder_selected)

    def select_county_outline():
        file_selected = filedialog.askopenfilename()
        county_outline.set(file_selected)

    # Define and arrange widgets here
    tk.Label(root, text="API Endpoints (comma separated)").grid(row=0, column=0)
    api_endpoints = tk.Entry(root, width=50)
    api_endpoints.grid(row=0, column=1)

    tk.Label(root, text="County Outline File").grid(row=1, column=0)
    county_outline = tk.StringVar()
    tk.Entry(root, textvariable=county_outline, width=50).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=select_county_outline).grid(row=1, column=2)

    tk.Label(root, text="Municipality Code").grid(row=2, column=0)
    municipality_code = tk.Entry(root, width=50)
    municipality_code.grid(row=2, column=1)

    tk.Label(root, text="Output Folder").grid(row=3, column=0)
    output_folder = tk.StringVar()
    tk.Entry(root, textvariable=output_folder, width=50).grid(row=3, column=1)
    tk.Button(root, text="Browse", command=select_output_folder).grid(row=3, column=2)

    tk.Button(root, text="Run", command=lambda: run_process(api_endpoints.get(), county_outline.get(), municipality_code.get(), output_folder.get())).grid(row=4, column=1)

    root.mainloop()

def run_process(api_endpoints, county_outline, municipality_code, output_folder):
    endpoints = api_endpoints.split(',')
    geojsons = [fetch_geojson(url) for url in endpoints]
    municipal_boundary = fetch_municipal_boundary(municipality_code)
    parcels = fetch_parcels(municipal_boundary)

    # Fetch ArcGIS REST API data
    roads = fetch_roads("https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Tran_road/FeatureServer/0", municipal_boundary)
    wetlands = fetch_wetlands("https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0", municipal_boundary)
    # Add more ArcGIS REST API data requests here if needed

    # Clip all data to the municipal boundary
    clipped_geojsons = [clip_to_boundary(geojson, municipal_boundary) for geojson in geojsons]
    clipped_geojsons.append(clip_to_boundary(municipal_boundary, municipal_boundary))
    clipped_geojsons.append(clip_to_boundary(parcels, municipal_boundary))
    clipped_geojsons.append(clip_to_boundary(roads, municipal_boundary))
    clipped_geojsons.append(clip_to_boundary(wetlands, municipal_boundary))
    # Add more clipped ArcGIS REST API data here if needed

    shapefiles = [save_shapefile(geojson, output_folder) for geojson in clipped_geojsons]
    group = create_arcgis_group()
    add_users(group, "users.xlsx")
    upload_shapefiles(group, shapefiles)
    log_operations(api_endpoints, output_folder, group.title)
