import tkinter as tk
from tkinter import filedialog

# Function to open a file dialog for selecting a CSV file
def browse_csv():
    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    csv_entry.delete(0, tk.END)  # Clear any existing text in the entry widget
    csv_entry.insert(0, filename)  # Insert the selected filename into the entry widget

# Function to open a directory dialog for selecting an output path
def browse_output_path():
    path = filedialog.askdirectory()
    output_path_entry.delete(0, tk.END)  # Clear any existing text in the entry widget
    output_path_entry.insert(0, path)  # Insert the selected path into the entry widget

# Function to handle submission of the form
def submit():
    township_name = township_name_entry.get()  # Get the text entered in the township name entry widget
    csv_file = csv_entry.get()  # Get the text entered in the CSV file entry widget
    output_path = output_path_entry.get()  # Get the text entered in the output path entry widget
    project_name = project_name_entry.get()  # Get the text entered in the project name entry widget

    # Optionally, print the values entered by the user
    #print("Township Name:", township_name)
    #print("CSV File:", csv_file)
    #print("Output Path:", output_path)
    #print("Project Name:", project_name)

# Create the main Tkinter window
root = tk.Tk()
root.title("SW Project Generator")  # Set the title of the window

# Increase the size of the window
root.geometry("292x175")

# Calculate the center of the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 500) // 2
y = (screen_height - 250) // 2

# Set the window to be centered on the screen
root.geometry("+{}+{}".format(x, y))

# Create labels and entry widgets for each input field
township_name_label = tk.Label(root, text="Township Name:")
township_name_label.grid(row=0, column=0, sticky="e")
township_name_entry = tk.Entry(root)
township_name_entry.grid(row=0, column=1, padx=5, pady=5)

csv_label = tk.Label(root, text="Users .CSV File:")
csv_label.grid(row=1, column=0, sticky="e")
csv_entry = tk.Entry(root)
csv_entry.grid(row=1, column=1, padx=5, pady=5)  # Add padding to the CSV entry widget
csv_button = tk.Button(root, text="Browse", command=browse_csv)
csv_button.grid(row=1, column=2, padx=5, pady=5)  # Add padding to the Browse button

output_path_label = tk.Label(root, text="Output Path:")
output_path_label.grid(row=2, column=0, sticky="e")
output_path_entry = tk.Entry(root)
output_path_entry.grid(row=2, column=1, padx=5, pady=5)  # Add padding to the output path entry widget
output_path_button = tk.Button(root, text="Browse", command=browse_output_path)
output_path_button.grid(row=2, column=2, padx=5, pady=5)  # Add padding to the Browse button

project_name_label = tk.Label(root, text="Project Name:")
project_name_label.grid(row=3, column=0, sticky="e")
project_name_entry = tk.Entry(root)
project_name_entry.grid(row=3, column=1, padx=5, pady=5)

# Create a submit button to submit the form
submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.grid(row=4, column=1, pady=10)

# Start the Tkinter event loop
root.mainloop()