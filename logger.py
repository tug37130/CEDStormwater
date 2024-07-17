import datetime

# Create an output text file in the output_folder that logs basic information such as the project number, output folder, time of completion, and API resources.
def log_operations(output_folder, project_number):
    with open(f"{output_folder}/SWAuto_Log_{project_number}.txt", "w") as log_file:
        log_file.write(f"Operations Log - {datetime.datetime.now()}\n")
        log_file.write(f"Output Folder: {output_folder}\n")
        log_file.write(f"Project Number: {project_number}\n")
        log_file.write("\nData Sources:\n")
        log_file.write(f"Wetlands: https://mapsdep.nj.gov/arcgis/rest/services/Features/Land_lu/MapServer/2/query\n")
        log_file.write(f"County: https://maps.nj.gov/arcgis/rest/services/Framework/Government_Boundaries/MapServer/1\n")
        log_file.write(f"Municipality: https://maps.nj.gov/arcgis/rest/services/Framework/Government_Boundaries/MapServer/2\n")
        log_file.write(f"Roads: https://maps.nj.gov/arcgis/rest/services/Framework/Transportation/MapServer/14\n")
        log_file.write(f"Parcels: https://services2.arcgis.com/XVOqAjTOJ5P6ngMu/ArcGIS/rest/services/Hosted_Parcels_Test_WebMer_20201016/FeatureServer/0\n")
