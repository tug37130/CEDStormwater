import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from geo_processor import reproject_shapefile, check_crs, clip_shapefile
from arcgis_online import create_arcgis_group, add_users, upload_shapefiles
from logger import log_operations
import logging
import os
import webbrowser
import sys
from api_handler import fetch_roads

logging.basicConfig(level=logging.INFO)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def launch_gui():
    root = tk.Tk()
    root.title("Geo Processing Application")

    def open_link(event):
        webbrowser.open_new(r"https://njogis-newjersey.opendata.arcgis.com/datasets/5f45e1ece6e14ef5866974a7b57d3b95/explore?showTable=true")

    def select_file(var):
        file_selected = filedialog.askopenfilename(filetypes=[("Shapefiles", "*.shp")])
        var.set(file_selected)

    def select_output_folder():
        folder_selected = filedialog.askdirectory()
        output_folder.set(folder_selected)

    # Adding the description and link at the top
    description = tk.Label(root, text="To find the GNIS code for a county in New Jersey, please refer to this")
    description.grid(row=0, column=0, columnspan=2, pady=(10, 10))
    link = tk.Label(root, text="link", fg="blue", cursor="hand2")
    link.grid(row=0, column=2, pady=(10, 10))
    link.bind("<Button-1>", open_link)

    tk.Label(root, text="Municipality Boundary").grid(row=1, column=0, sticky="e")
    municipality_boundary_file = tk.StringVar()
    tk.Entry(root, textvariable=municipality_boundary_file, width=50).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=lambda: select_file(municipality_boundary_file)).grid(row=1, column=2)

    tk.Label(root, text="Parcels Layer").grid(row=2, column=0, sticky="e")
    parcels_file = tk.StringVar()
    tk.Entry(root, textvariable=parcels_file, width=50).grid(row=2, column=1)
    tk.Button(root, text="Browse", command=lambda: select_file(parcels_file)).grid(row=2, column=2)

    tk.Label(root, text="Wetlands Layer").grid(row=3, column=0, sticky="e")
    wetlands_file = tk.StringVar()
    tk.Entry(root, textvariable=wetlands_file, width=50).grid(row=3, column=1)
    tk.Button(root, text="Browse", command=lambda: select_file(wetlands_file)).grid(row=3, column=2)

    tk.Label(root, text="Output Folder").grid(row=4, column=0, sticky="e")
    output_folder = tk.StringVar()
    tk.Entry(root, textvariable=output_folder, width=50).grid(row=4, column=1)
    tk.Button(root, text="Browse", command=select_output_folder).grid(row=4, column=2)

    tk.Label(root, text="GNIS Code for County").grid(row=5, column=0, sticky="e")
    gnis_code = tk.StringVar()
    tk.Entry(root, textvariable=gnis_code, width=50).grid(row=5, column=1)

    tk.Button(root, text="Run", command=lambda: run_process(
        municipality_boundary_file.get(),
        parcels_file.get(),
        wetlands_file.get(),
        output_folder.get(),
        gnis_code.get()
    )).grid(row=6, column=1, pady=(10, 10))

    root.mainloop()

def run_process(municipality_boundary_file, parcels_file, wetlands_file, output_folder, gnis_code):
    try:
        target_crs = "EPSG:4326"

        def ensure_crs(file_path, output_name):
            if not check_crs(file_path, target_crs):
                output_path = os.path.join(output_folder, output_name)
                return reproject_shapefile(file_path, output_path, target_crs)
            return file_path

        logging.info("Checking and reprojecting shapefiles to target CRS if necessary...")
        municipality_boundary_file = ensure_crs(municipality_boundary_file, "reprojected_municipality_boundary.shp")
        parcels_file = ensure_crs(parcels_file, "reprojected_parcels.shp")
        wetlands_file = ensure_crs(wetlands_file, "reprojected_wetlands.shp")

        logging.info("Fetching roads data from ArcGIS REST service...")
        roads_gdf = fetch_roads(
            "https://maps.nj.gov/arcgis/rest/services/Framework/Transportation/MapServer/14",
            f"COUNTY_L='{gnis_code}'"
        )
        roads_file = os.path.join(output_folder, "fetched_roads.shp")
        roads_gdf.to_file(roads_file)
        logging.info("Roads data fetched and saved successfully")

        logging.info("Clipping roads layer to municipal boundary...")
        clipped_roads_file = clip_shapefile(roads_file, municipality_boundary_file, os.path.join(output_folder, "clipped_roads.shp"))
        logging.info("Roads layer clipped successfully")

        logging.info("Clipping parcels layer to municipal boundary...")
        clipped_parcels_file = clip_shapefile(parcels_file, municipality_boundary_file, os.path.join(output_folder, "clipped_parcels.shp"))
        logging.info("Parcels layer clipped successfully")

        logging.info("Clipping wetlands layer to municipal boundary...")
        clipped_wetlands_file = clip_shapefile(wetlands_file, municipality_boundary_file, os.path.join(output_folder, "clipped_wetlands.shp"))
        logging.info("Wetlands layer clipped successfully")

        username = simpledialog.askstring("Input", "Enter your ArcGIS Online username:")
        password = simpledialog.askstring("Input", "Enter your ArcGIS Online password:", show='*')
        group_name = simpledialog.askstring("Input", "Enter the name for the new ArcGIS Online group:")

        logging.info("Creating ArcGIS group...")
        group = create_arcgis_group(username, password, group_name)
        logging.info("ArcGIS group created successfully")

        logging.info("Adding users to group...")
        add_users(group, "users.xlsx")
        logging.info("Users added to group successfully")

        logging.info("Uploading shapefiles to ArcGIS Online...")
        upload_shapefiles(group, [clipped_roads_file, clipped_parcels_file, clipped_wetlands_file])
        logging.info("Shapefiles uploaded to ArcGIS Online successfully")

        log_operations(municipality_boundary_file, output_folder, group.title)
        logging.info("Process completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    launch_gui()
