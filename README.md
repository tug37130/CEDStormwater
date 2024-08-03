## Table of Contents

- Requirements
- Installation
- Configuration
- Troubleshooting
- FAQ
##
## Requirements

This module requires installation of the following modules:
- tkinter (standard Python interface to the Tcl/Tk GUI toolkit: [documentation](https://docs.python.org/3/library/tkinter.html))
- geopandas (open source project to add support for geographic data to pandas objects: [documentation](https://geopandas.org/en/stable/about.html))
- logging (flexible event logging system: [documentation](https://docs.python.org/3/library/logging.html))
- webbrowser (high-level interface to allow displaying web-based documents: [documentation](https://docs.python.org/3/library/webbrowser.html))
- sys (provides access to some variables used or maintained by the interpreter: [documentation](https://docs.python.org/3/library/sys.html))
- os (provides a portable way of using operating system dependent functionality: [documentation](https://docs.python.org/3/library/os.html))
##
## Installation

If running the executable:
1. Download and Save the .exe File
    - In the GitHub repository, select and download the .exe file. This will be labeled as "SWLayerGenerator"
    - Save the executable to an accessible location such as your Desktop or Documents.
        - Please refrain from saving this in a project folder.

2. Run the Application
    - Double-click the executable file.
##
If running source code in an IDE:
1. Install Anaconda
- Navigate to [Anaconda's distribution page](https://www.anaconda.com/download).
    - Login, or signup to obtain access to access the distribution.
    - Once signed-in, navigate to "products" in the top ribbon and select the "individual edition."
    - Select the proper installation version (i.e. Windows 64-Bit Graphical Installer).
    - Once downloaded, run the installer and keep all defaults.
 
2. Virtual Environment Creation
- Launch the previously installed Anaconda Prompt.
- Input the following code, running each line individually:
    - `conda create --name ced`
    - `conda activate ced`
    - `pip install geopandas tkinter logging webbrowser`

 3. Running the Application
- Open all source code files.
- Run all files, except for main.py and gui.py, to set the functions.
- Initiate/run the program by running either the main.py or gui.py.
##
## Configuration

User Inputs:
- Output Folder: The folder in which all data will be saved. Clicking the "Browse" button will open a file explorer window where the user can select a folder.
    - Note: This would be a "Data" folder in a project folder. All generated layers will save into subfolders with standardized naming (ex: Parcels_23007605G).
- County Name: The name of the County of the project.
    - Note: This input should not include "County," only the proper name is required (ex: Atlantic, Essex). Please see [NJGIN](https://njogis-newjersey.opendata.arcgis.com/datasets/5f45e1ece6e14ef5866974a7b57d3b95/explore?showTable=true).
- Municipality Code: The four digit code for the desired municipality (ex: 0102). Please see [nj.gov](https://www.nj.gov/treasury/taxation/pdf/lpt/cntycode.pdf).
- Municipality Name: The name of the project's municipality (ex: Atlantic City).
- GNIS Code for County: The six digit GNIS code for the county (ex: 882270). Please see [NJGIN](https://njogis-newjersey.opendata.arcgis.com/datasets/5f45e1ece6e14ef5866974a7b57d3b95/explore?showTable=true).
- Project Number: CED project number.
##
## Troubleshooting

Common Issues and Resolution:

"Error: Please ensure county name is correct."
- The county name given is incorrect.
    - The county name you put in should not include "County of ..." or "... County." Please list only the proper name of the county (ex: "Atlantic")
    - This could also be a simple misspelling of the county name.
 
"Error: Please ensure municipality code is correct."
- The municipality code given is incorrect.
    - This should be a four digit code. (ex: "0102" for Atlantic City)
    - This could also be a simple mistype.

"Error: Please ensure GNIS code is correct."
- The GNIS code is incorrect.
    - This should be a six-digit code. (ex: "882270" for Atlantic County)
    - This could also be a simple mistype.
 
NOTE: Once an error dialogue is given, clicking the "Ok" button will remove any previously created files and keep the application open. Once the error dialogue is closed the given error can be fixed and can be re-run.
##
## Frequently Asked Questions (FAQ)

Can this application be run while not connected to the internet?
- No. This application requires internet access to request and save all data from the APIs.

Do you need to be on the corporate VPN, or in office to run the application?
- You do need to be connected to the corporate VPN to execute the application, as data will normally be saved on the coporate file system (i.e. into a project folder). If you run the application locally and save the data locally, you do not need to be connected to the corporate VPN.
- You do not need to be in the office to run the application.

Where do the files go once the application is ran?
- All files generated by the application will save into subfolders in the given output folder. For example, if you set the output folder to "C:/Project1/Data" all files will be saved in various subfolders "C:/Project1/Data/Parcels_Project1".

Is the data updated automatically?
- The application will always use the newest data available through the API.
##

