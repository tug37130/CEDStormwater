import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from geo_processor import reproject_shapefile, check_crs, clip_shapefile
from logger import log_operations
from api_handler import fetch_county_boundary, fetch_parcels, fetch_roads, fetch_municipality_boundary
import logging
import os
import webbrowser
import sys

logging.basicConfig(level=logging.INFO)

def resource_path(relative_path):
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

    description = tk.Label(root, text="To find the GNIS code for a county in New Jersey, please refer to this")
    description.grid(row=0, column=0, columnspan=2, pady=(10, 10))
    link = tk.Label(root, text="link", fg="blue", cursor="hand2")
    link.grid(row=0, column=2, pady=(10, 10))
    link.bind("<Button-1>", open_link)

    tk.Label(root, text="Wetlands Layer").grid(row=1, column=0, sticky="e")
    wetlands_file = tk.StringVar()
    tk.Entry(root, textvariable=wetlands_file, width=50).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=lambda: select_file(wetlands_file)).grid(row=1, column=2)

    tk.Label(root, text="Output Folder").grid(row=2, column=0, sticky="e")
    output_folder = tk.StringVar()
    tk.Entry(root, textvariable=output_folder, width=50).grid(row=2, column=1)
    tk.Button(root, text="Browse", command=select_output_folder).grid(row=2, column=2)

    tk.Label(root, text="County Name (ex: Atlantic)").grid(row=3, column=0, sticky="e")
    county_name = tk.StringVar()
    tk.Entry(root, textvariable=county_name, width=50).grid(row=3, column=1)

    tk.Label(root, text="Municipality Code").grid(row=4, column=0, sticky="e")
    municipality_code = tk.StringVar()
    tk.Entry(root, textvariable=municipality_code, width=50).grid(row=4, column=1)

    tk.Label(root, text="Municipality Name").grid(row=5, column=0, sticky="e")
    municipality_name = tk.StringVar()
    tk.Entry(root, textvariable=municipality_name, width=50).grid(row=5, column=1)

    tk.Label(root, text="GNIS Code for County").grid(row=6, column=0, sticky="e")
    gnis_code = tk.StringVar()
    tk.Entry(root, textvariable=gnis_code, width=50).grid(row=6, column=1)

    tk.Label(root, text="Project Number").grid(row=7, column=0, sticky="e")
    project_number = tk.StringVar()
    tk.Entry(root, textvariable=project_number, width=50).grid(row=7, column=1)

    tk.Button(root, text="Run", command=lambda: run_process(
        wetlands_file.get(),
        output_folder.get(),
        county_name.get(),
        municipality_code.get(),
        municipality_name.get(),
        gnis_code.get(),
        project_number.get()
    )).grid(row=8, column=1, pady=(10, 10))

    root.mainloop()

def run_process(wetlands_file, output_folder, county_name, municipality_code, municipality_name, gnis_code, project_number):
    try:
        target_crs = "EPSG:4326"

        def ensure_crs(file_path, output_name):
            if not check_crs(file_path, target_crs):
                output_path = os.path.join(output_folder, output_name)
                return reproject_shapefile(file_path, output_path, target_crs)
            return file_path

        logging.info("Checking and reprojecting shapefiles to target CRS if necessary...")
        wetlands_file = ensure_crs(wetlands_file, "reprojected_wetlands.shp")

        logging.info("Fetching county boundary data from ArcGIS REST service...")
        county_boundary_file = fetch_county_boundary(county_name, output_folder, project_number)
        logging.info("County boundary data fetched and saved successfully")

        logging.info("Reprojecting county boundary to target CRS if necessary...")
        county_boundary_file = ensure_crs(county_boundary_file, f"reprojected_County_of_{county_name}_Boundary_{project_number}.shp")
        logging.info("County boundary reprojected successfully")

        logging.info("Fetching parcels data from ArcGIS REST service...")
        parcels_file = fetch_parcels(municipality_code, output_folder, project_number)
        logging.info("Parcels data fetched and saved successfully")

        logging.info("Reprojecting parcels to target CRS if necessary...")
        parcels_file = ensure_crs(parcels_file, f"reprojected_Parcels_{project_number}.shp")
        logging.info("Parcels reprojected successfully")

        logging.info("Fetching roads data from ArcGIS REST service...")
        roads_file = fetch_roads(gnis_code, output_folder, project_number)
        logging.info("Roads data fetched and saved successfully")

        logging.info("Reprojecting roads to target CRS if necessary...")
        roads_file = ensure_crs(roads_file, f"reprojected_Roads_{project_number}.shp")
        logging.info("Roads reprojected successfully")

        logging.info("Fetching municipality boundary data from ArcGIS REST service...")
        municipality_boundary_file = fetch_municipality_boundary(municipality_code, output_folder, municipality_name, project_number)
        logging.info("Municipality boundary data fetched and saved successfully")

        logging.info("Reprojecting municipality boundary to target CRS if necessary...")
        municipality_boundary_file = ensure_crs(municipality_boundary_file, f"reprojected_{municipality_name.replace(' ', '_')}_Boundary_{project_number}.shp")
        logging.info("Municipality boundary reprojected successfully")

        logging.info("Clipping roads layer to municipality boundary...")
        clipped_roads_file = clip_shapefile(roads_file, municipality_boundary_file, os.path.join(output_folder, f"Roads_{project_number}", f"Roads_{project_number}.shp"))
        logging.info("Roads layer clipped successfully")

        logging.info("Clipping parcels layer to municipality boundary...")
        clipped_parcels_file = clip_shapefile(parcels_file, municipality_boundary_file, os.path.join(output_folder, f"Parcels_{project_number}", f"Parcels_{project_number}.shp"))
        logging.info("Parcels layer clipped successfully")

        logging.info("Clipping wetlands layer to municipality boundary...")
        clipped_wetlands_file = clip_shapefile(wetlands_file, municipality_boundary_file, os.path.join(output_folder, f"Wetlands_{project_number}", f"Wetlands_{project_number}.shp"))
        logging.info("Wetlands layer clipped successfully")

        for file_path in [county_boundary_file, parcels_file, roads_file, municipality_boundary_file, wetlands_file]:
            try:
                os.remove(file_path)
                for ext in ['.cpg', '.dbf', '.prj', '.shx']:
                    os.remove(file_path.replace('.shp', ext))
                logging.info(f"Removed intermediary file: {file_path}")
            except Exception as e:
                logging.error(f"An error occurred while removing {file_path.replace('.shp', ext)}: {e}")

        log_operations(output_folder, project_number)
        logging.info("Process completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    launch_gui()
