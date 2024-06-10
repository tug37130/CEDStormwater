import tkinter as tk
from tkinter import simpledialog, filedialog
from api_handler import (
    fetch_municipal_boundary, fetch_parcels,
    fetch_roads, fetch_wetlands
)
from geo_processor import clip_to_boundary
from file_manager import save_shapefile
from arcgis_online import create_arcgis_group, add_users, upload_shapefiles
from logger import log_operations

def launch_gui():
    root = tk.Tk()
    root.title("Geo Processing Application")

    def select_output_folder():
        folder_selected = filedialog.askdirectory()
        output_folder.set(folder_selected)

    # Define and arrange widgets here
    tk.Label(root, text="Municipality Code").grid(row=0, column=0)
    municipality_code = tk.Entry(root, width=50)
    municipality_code.grid(row=0, column=1)

    tk.Label(root, text="Output Folder").grid(row=1, column=0)
    output_folder = tk.StringVar()
    tk.Entry(root, textvariable=output_folder, width=50).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=select_output_folder).grid(row=1, column=2)

    tk.Button(root, text="Run", command=lambda: run_process(municipality_code.get(), output_folder.get())).grid(row=2, column=1)

    root.mainloop()

def run_process(municipality_code, output_folder):
    username = simpledialog.askstring("Input", "Enter your ArcGIS Online username:")
    password = simpledialog.askstring("Input", "Enter your ArcGIS Online password:", show='*')
    group_name = simpledialog.askstring("Input", "Enter the name for the new ArcGIS Online group:")

    municipal_boundary = fetch_municipal_boundary(municipality_code)
    parcels_data = fetch_parcels(municipality_code)
    roads_data = fetch_roads("https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Tran_road/FeatureServer/0", municipal_boundary)
    wetlands_data = fetch_wetlands("https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Wetlands/FeatureServer/0", municipal_boundary)

    # Clip all data to the municipal boundary
    clipped_geojsons = []
    clipped_geojsons.append(clip_to_boundary(municipal_boundary, municipal_boundary))
    clipped_geojsons.append(clip_to_boundary(parcels_data, municipal_boundary))
    clipped_geojsons.append(clip_to_boundary(roads_data, municipal_boundary))
    clipped_geojsons.append(clip_to_boundary(wetlands_data, municipal_boundary))

    shapefiles = [save_shapefile(gdf, output_folder) for gdf in clipped_geojsons]
    group = create_arcgis_group(username, password, group_name)
    add_users(group, "users.xlsx")
    upload_shapefiles(group, shapefiles)
    log_operations(municipality_code, output_folder, group.title)

if __name__ == "__main__":
    launch_gui()
