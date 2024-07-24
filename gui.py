import tkinter as tk
from tkinter import filedialog, messagebox
from geo_processor import reproject_shapefile, check_crs, clip_shapefile
from logger import log_operations
from api_handler import (
    fetch_county_boundary,
    fetch_parcels,
    fetch_roads,
    fetch_municipality_boundary,
    fetch_wetlands_within_boundary,
    fetch_neighboring_municipalities,
    fetch_waterbodies_within_boundary
)
import geopandas as gpd
import logging
import os
import webbrowser
import sys
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to get the resource path
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Launch the GUI
def launch_gui():
    root = tk.Tk()
    root.title("Stormwater Layer Generator")

    # Function to open a link to the documentation
    def open_link(event):
        webbrowser.open_new(r"https://github.com/tug37130/CEDStormwater/blob/main/README.md")

    # Function to select the output folder
    def select_output_folder():
        folder_selected = filedialog.askdirectory()
        output_folder.set(folder_selected)

    # Create and place widgets in the GUI
    # Create a frame to hold the description and ReadMe link
    frame = tk.Frame(root)
    frame.grid(row=0, column=0, columnspan=3, pady=(10, 10))

    description = tk.Label(frame, text="For more information, please refer to the application's")
    description.pack(side=tk.LEFT)

    link = tk.Label(frame, text="ReadMe", fg="blue", cursor="hand2")
    link.pack(side=tk.LEFT)
    link.bind("<Button-1>", open_link)

    # Output folder dialogue
    tk.Label(root, text="Output Folder").grid(row=1, column=0, sticky="e")
    output_folder = tk.StringVar()
    tk.Entry(root, textvariable=output_folder, width=50).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=select_output_folder).grid(row=1, column=2)

    # County name dialouge
    tk.Label(root, text="County Name (ex: Atlantic)").grid(row=2, column=0, sticky="e")
    county_name = tk.StringVar()
    tk.Entry(root, textvariable=county_name, width=50).grid(row=2, column=1)

    # Municipality code dialogue
    tk.Label(root, text="Municipality Code").grid(row=3, column=0, sticky="e")
    municipality_code = tk.StringVar()
    tk.Entry(root, textvariable=municipality_code, width=50).grid(row=3, column=1)

    # Municipality name dialogue
    tk.Label(root, text="Municipality Name").grid(row=4, column=0, sticky="e")
    municipality_name = tk.StringVar()
    tk.Entry(root, textvariable=municipality_name, width=50).grid(row=4, column=1)

    # GNIS dialogue
    tk.Label(root, text="GNIS Code for County").grid(row=5, column=0, sticky="e")
    gnis_code = tk.StringVar()
    tk.Entry(root, textvariable=gnis_code, width=50).grid(row=5, column=1)

    # Project number dialogue
    tk.Label(root, text="Project Number").grid(row=6, column=0, sticky="e")
    project_number = tk.StringVar()
    tk.Entry(root, textvariable=project_number, width=50).grid(row=6, column=1)

    # Initiate application once the "Run" button is clicked
    tk.Button(
        root,
        text="Run",
        command=lambda: run_process(
            output_folder.get(),
            county_name.get(),
            municipality_code.get(),
            municipality_name.get(),
            gnis_code.get(),
            project_number.get(),
        ),
    ).grid(row=7, column=1, pady=(10, 10))

    root.mainloop()

# Function to display the success message
def show_success_message(output_folder):
    success_window = tk.Toplevel()
    success_window.title("Process Complete")
    tk.Label(success_window, text=f"Application complete: data saved in {output_folder}").pack(pady=20, padx=20)
    tk.Button(success_window, text="OK", command=success_window.destroy).pack(pady=(0, 20))

# Primary function to run the application
def run_process(
    output_folder, county_name, municipality_code, municipality_name, gnis_code, project_number
):
    created_files = []
    wetlands_files = []
    neighboring_files = []
    waterbodies_files = []
    parcels_files = []
    roads_files = []

    try:
        target_crs = "EPSG:4326"

        # Function to ensure the CRS of a file is correct
        def ensure_crs(file_path, output_name):
            if not check_crs(file_path, target_crs):
                output_path = os.path.join(output_folder, output_name)
                created_files.append(output_path)
                return reproject_shapefile(file_path, output_path, target_crs)
            return file_path

        logging.info("Checking and reprojecting shapefiles to target CRS if necessary...")

        # Fetch and process county boundary data
        logging.info("Fetching county boundary data from ArcGIS REST service...")
        try:
            county_boundary_file = fetch_county_boundary(
                county_name, output_folder, project_number
            )
            if county_boundary_file is None:
                raise ValueError("Error: Please ensure county name is correct")
            created_files.append(county_boundary_file)
            logging.info("County boundary data fetched and saved successfully")
        except Exception as e:
            raise ValueError("Error: Please ensure county name is correct") from e

        logging.info("Reprojecting county boundary to target CRS if necessary...")
        county_boundary_file = ensure_crs(
            county_boundary_file, f"reprojected_County_of_{county_name}_Boundary_{project_number}.shp"
        )
        logging.info("County boundary reprojected successfully")

        # Fetch and process parcels data
        logging.info("Fetching parcels data from ArcGIS REST service...")
        try:
            parcels_file = fetch_parcels(municipality_code, output_folder, project_number)
            if parcels_file is None:
                raise ValueError("Error: Please ensure municipality code is correct")
            parcels_files.append(parcels_file)
            for ext in [".cpg", ".dbf", ".prj", ".shx"]:
                parcels_files.append(parcels_file.replace(".shp", ext))
            logging.info("Parcels data fetched and saved successfully")
        except Exception as e:
            raise ValueError("Error: Please ensure municipality code is correct") from e

        logging.info("Reprojecting parcels to target CRS if necessary...")
        parcels_file = ensure_crs(parcels_file, f"reprojected_Parcels_{project_number}.shp")
        logging.info("Parcels reprojected successfully")

        # Fetch and process roads data
        logging.info("Fetching roads data from ArcGIS REST service...")
        try:
            roads_file = fetch_roads(gnis_code, output_folder, project_number)
            if roads_file is None:
                raise ValueError("Error: Please ensure GNIS code is correct")
            roads_files.append(roads_file)
            for ext in [".cpg", ".dbf", ".prj", ".shx"]:
                roads_files.append(roads_file.replace(".shp", ext))
            logging.info("Roads data fetched and saved successfully")
        except Exception as e:
            raise ValueError("Error: Please ensure GNIS code is correct") from e

        logging.info("Reprojecting roads to target CRS if necessary...")
        roads_file = ensure_crs(roads_file, f"reprojected_Roads_{project_number}.shp")
        logging.info("Roads reprojected successfully")

        # Fetch and process municipality boundary data
        logging.info("Fetching municipality boundary data from ArcGIS REST service...")
        try:
            municipality_boundary_file = fetch_municipality_boundary(
                municipality_code, output_folder, municipality_name, project_number
            )
            if municipality_boundary_file is None:
                raise ValueError("Error: Please ensure municipality name and code are correct")
            created_files.append(municipality_boundary_file)
            logging.info("Municipality boundary data fetched and saved successfully")
        except Exception as e:
            raise ValueError("Error: Please ensure municipality name and code are correct") from e

        logging.info("Reprojecting municipality boundary to target CRS if necessary...")
        municipality_boundary_file = ensure_crs(
            municipality_boundary_file,
            f"reprojected_{municipality_name.replace(' ', '_')}_Boundary_{project_number}.shp",
        )
        logging.info("Municipality boundary reprojected successfully")

        # Fetch and process wetlands data
        logging.info("Fetching wetlands data from ArcGIS REST service...")
        try:
            municipality_boundary_gdf = gpd.read_file(municipality_boundary_file)
            wetlands_file = fetch_wetlands_within_boundary(
                municipality_boundary_gdf, output_folder, project_number
            )
            if wetlands_file is None:
                raise ValueError("Error: Failed to fetch wetlands data")
            wetlands_files.append(wetlands_file)
            for ext in [".cpg", ".dbf", ".prj", ".shx"]:
                wetlands_files.append(wetlands_file.replace(".shp", ext))
            logging.info(f"Wetlands data fetched and saved successfully: {wetlands_file}")
        except Exception as e:
            raise ValueError("Error: Failed to fetch wetlands data") from e

        # Fetch and process neighboring municipalities data
        logging.info("Fetching neighboring municipalities data from ArcGIS REST service...")
        try:
            neighboring_file = fetch_neighboring_municipalities(
                municipality_boundary_gdf, output_folder, project_number
            )
            if neighboring_file is None:
                raise ValueError("Error: Failed to fetch neighboring municipalities data")
            neighboring_files.append(neighboring_file)
            for ext in [".cpg", ".dbf", ".prj", ".shx"]:
                neighboring_files.append(neighboring_file.replace(".shp", ext))
            logging.info(
                f"Neighboring municipalities data fetched and saved successfully: {neighboring_file}"
            )
        except Exception as e:
            raise ValueError("Error: Failed to fetch neighboring municipalities data") from e

        # Fetch and process waterbodies
        logging.info("Fetching waterbodies data from ArcGIS REST service...")
        try:
            waterbodies_file = fetch_waterbodies_within_boundary(
                municipality_boundary_gdf, output_folder, project_number
            )
            if waterbodies_file is None:
                raise ValueError("Error: Failed to fetch waterbodies data")
            waterbodies_files.append(waterbodies_file)
            for ext in [".cpg", ".dbf", ".prj", ".shx"]:
                waterbodies_files.append(waterbodies_file.replace(".shp", ext))
            logging.info(f"Waterbodies data fetched and saved successfully: {waterbodies_file}")
        except Exception as e:
            raise ValueError("Error: Failed to fetch waterbodies data") from e

        # Clip roads layer to municipality boundary
        logging.info("Clipping roads layer to municipality boundary...")
        clipped_roads_file = clip_shapefile(
            roads_file,
            municipality_boundary_file,
            os.path.join(output_folder, f"Roads_{project_number}", f"Roads_{project_number}.shp"),
        )
        logging.info("Roads layer clipped successfully")

        # Clip parcels layer to municipality boundary
        logging.info("Clipping parcels layer to municipality boundary...")
        clipped_parcels_file = clip_shapefile(
            parcels_file,
            municipality_boundary_file,
            os.path.join(
                output_folder, f"Parcels_{project_number}", f"Parcels_{project_number}.shp"
            ),
        )
        logging.info("Parcels layer clipped successfully")

        # Move and organize files into subfolders using the given file's basename. Ensure data does not appear in the output folder location.
        for file_path in created_files:
            try:
                dir_name = os.path.basename(file_path).replace("reprojected_", "").replace(
                    ".shp", ""
                )
                layer_output_folder = os.path.join(output_folder, dir_name)
                if not os.path.exists(layer_output_folder):
                    os.makedirs(layer_output_folder)
                for ext in [".shp", ".cpg", ".dbf", ".prj", ".shx"]:
                    base_file = file_path.replace(".shp", ext)
                    if os.path.exists(base_file):
                        shutil.move(base_file, os.path.join(layer_output_folder, os.path.basename(base_file)))
                logging.info(f"Moved files to: {layer_output_folder}")
            except Exception as e:
                logging.error(f"An error occurred while moving {file_path}: {e}")

        for file_path in wetlands_files:
            try:
                dir_name = f"Wetlands_{project_number}"
                layer_output_folder = os.path.join(output_folder, dir_name)
                if not os.path.exists(layer_output_folder):
                    os.makedirs(layer_output_folder)
                for ext in [".shp", ".cpg", ".dbf", ".prj", ".shx"]:
                    base_file = file_path.replace(".shp", ext)
                    if os.path.exists(base_file):
                        shutil.move(base_file, os.path.join(layer_output_folder, os.path.basename(base_file)))
                logging.info(f"Moved files to: {layer_output_folder}")
            except Exception as e:
                logging.error(f"An error occurred while moving wetlands file: {e}")

        for file_path in neighboring_files:
            try:
                dir_name = f"Neighboring_Municipalities_{project_number}"
                layer_output_folder = os.path.join(output_folder, dir_name)
                if not os.path.exists(layer_output_folder):
                    os.makedirs(layer_output_folder)
                for ext in [".shp", ".cpg", ".dbf", ".prj", ".shx"]:
                    base_file = file_path.replace(".shp", ext)
                    if os.path.exists(base_file):
                        shutil.move(base_file, os.path.join(layer_output_folder, os.path.basename(base_file)))
                logging.info(f"Moved files to: {layer_output_folder}")
            except Exception as e:
                logging.error(f"An error occurred while moving neighboring municipalities file: {e}")

        for file_path in waterbodies_files:
            try:
                dir_name = f"Waterbodies_{project_number}"
                layer_output_folder = os.path.join(output_folder, dir_name)
                if not os.path.exists(layer_output_folder):
                    os.makedirs(layer_output_folder)
                for ext in [".shp", ".cpg", ".dbf", ".prj", ".shx"]:
                    base_file = file_path.replace(".shp", ext)
                    if os.path.exists(base_file):
                        shutil.move(base_file, os.path.join(layer_output_folder, os.path.basename(base_file)))
                logging.info(f"Moved files to: {layer_output_folder}")
            except Exception as e:
                logging.error(f"An error occurred while moving waterbodies file: {e}")

        for file_path in parcels_files:
            try:
                dir_name = f"Parcels_{project_number}"
                layer_output_folder = os.path.join(output_folder, dir_name)
                if not os.path.exists(layer_output_folder):
                    os.makedirs(layer_output_folder)
                for ext in [".shp", ".cpg", ".dbf", ".prj", ".shx"]:
                    base_file = file_path.replace(".shp", ext)
                    if os.path.exists(base_file):
                        shutil.move(base_file, os.path.join(layer_output_folder, os.path.basename(base_file)))
                logging.info(f"Moved files to: {layer_output_folder}")
            except Exception as e:
                logging.error(f"An error occurred while moving parcels file: {e}")

        for file_path in roads_files:
            try:
                dir_name = f"Roads_{project_number}"
                layer_output_folder = os.path.join(output_folder, dir_name)
                if not os.path.exists(layer_output_folder):
                    os.makedirs(layer_output_folder)
                for ext in [".shp", ".cpg", ".dbf", ".prj", ".shx"]:
                    base_file = file_path.replace(".shp", ext)
                    if os.path.exists(base_file):
                        shutil.move(base_file, os.path.join(layer_output_folder, os.path.basename(base_file)))
                logging.info(f"Moved files to: {layer_output_folder}")
            except Exception as e:
                logging.error(f"An error occurred while moving roads file: {e}")

        # Remove intermediary files (ex: reprojected/clipped layers)
        for file_path in created_files:
            try:
                os.remove(file_path)
                for ext in [".cpg", ".dbf", ".prj", ".shx"]:
                    os.remove(file_path.replace(".shp", ext))
                logging.info(f"Removed intermediary file: {file_path}")
            except Exception as e:
                logging.error(f"An error occurred while removing {file_path}: {e}")

        # Remove empty directories if necessary
        for root, dirs, files in os.walk(output_folder):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    logging.info(f"Removed empty directory: {dir_path}")

        log_operations(output_folder, project_number)
        logging.info("Process completed successfully")
        
        # Show success message
        show_success_message(output_folder)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", str(e))

        # If the application does not run properly, remove any created files. Ensure the user does not need to manually remove any files that were created.
        for file_path in created_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    for ext in [".cpg", ".dbf", ".prj", ".shx"]:
                        os.remove(file_path.replace(".shp", ext))
                    logging.info(f"Removed file due to error: {file_path}")
            except Exception as ex:
                logging.error(f"An error occurred while deleting file {file_path}: {ex}")

        for file_path in wetlands_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"Removed wetlands file due to error: {file_path}")
            except Exception as ex:
                logging.error(f"An error occurred while deleting wetlands file {file_path}: {ex}")

        for file_path in neighboring_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"Removed neighboring municipalities file due to error: {file_path}")
            except Exception as ex:
                logging.error(f"An error occurred while deleting neighboring municipalities file {file_path}: {ex}")

        for file_path in waterbodies_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"Removed waterbodies file due to error: {file_path}")
            except Exception as ex:
                logging.error(f"An error occurred while deleting waterbodies file {file_path}: {ex}")

        for file_path in parcels_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"Removed parcels file due to error: {file_path}")
            except Exception as ex:
                logging.error(f"An error occurred while deleting parcels file {file_path}: {ex}")

        for file_path in roads_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"Removed roads file due to error: {file_path}")
            except Exception as ex:
                logging.error(f"An error occurred while deleting roads file {file_path}: {ex}")

        for root, dirs, files in os.walk(output_folder):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    shutil.rmtree(dir_path)
                    logging.info(f"Removed directory due to error: {dir_path}")
                except Exception as ex:
                    logging.error(f"An error occurred while deleting directory {dir_path}: {ex}")

if __name__ == "__main__":
    launch_gui()
