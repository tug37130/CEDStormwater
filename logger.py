import datetime

def log_operations(api_endpoints, output_folder, group_name):
    with open(f"{output_folder}/log.txt", "w") as log_file:
        log_file.write(f"Operations Log - {datetime.datetime.now()}\n")
        log_file.write(f"API Endpoints: {api_endpoints}\n")
        log_file.write(f"Output Folder: {output_folder}\n")
        log_file.write(f"ArcGIS Online Group: {group_name}\n")
