import datetime

def log_operations(output_folder, project_number):
    with open(f"{output_folder}/log_{project_number}.txt", "w") as log_file:
        log_file.write(f"Operations Log - {datetime.datetime.now()}\n")
        log_file.write(f"Output Folder: {output_folder}\n")
        log_file.write(f"Project Number: {project_number}\n")
