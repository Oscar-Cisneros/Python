#File Extractor

import os
import zipfile
import shutil

# Define paths
downloads_folder = os.path.expanduser("~/Downloads")
destination_folder = 'C:\\Users\\{Username}\\{Directory}'  # Change this to your desired destination

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# List all .zip files in the Downloads directory
zip_files = [f for f in os.listdir(downloads_folder) if f.lower().endswith('.zip')]

for zip_file_name in zip_files:
    # Construct the full path to the ZIP file
    zip_file_path = os.path.join(downloads_folder, zip_file_name)

    # Determine the name of the folder to extract to
    extracted_folder_name = os.path.splitext(zip_file_name)[0]
    extracted_folder_path = os.path.join(downloads_folder, extracted_folder_name)

    # Check if the specified ZIP file exists
    if os.path.isfile(zip_file_path) and zipfile.is_zipfile(zip_file_path):
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Create the extracted folder
            os.makedirs(extracted_folder_path, exist_ok=True)
            
            # Loop through each file in the zip file
            for file_info in zip_ref.infolist():
                # Check if it's a file and not inside a subfolder
                if file_info.is_dir() or os.path.dirname(file_info.filename):
                    continue

                # Extract only the top-level files to the new folder
                extracted_file_path = os.path.join(extracted_folder_path, os.path.basename(file_info.filename))
                with zip_ref.open(file_info.filename) as source, open(extracted_file_path, "wb") as target:
                    shutil.copyfileobj(source, target)
        
        # Move the extracted folder to the destination folder
        shutil.move(extracted_folder_path, os.path.join(destination_folder, extracted_folder_name))
        print(f"ZIP file '{zip_file_name}' has been extracted (top-level files only) to '{extracted_folder_name}' and moved successfully.")
    else:
        print(f"Error: The file '{zip_file_name}' does not exist or is not a valid ZIP file.")

################################### Test With Static Files if desired ####################################################################
import os
import zipfile
import shutil

# Define paths
downloads_folder = os.path.expanduser("~/Downloads")
destination_folder = 'C:\\Users\\{Username}\\{Directory}'  # Change this to your desired destination

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# List of ZIP files to process
zip_files = ['Test.zip', 'Test3.zip']  # Add your ZIP file names here

for zip_file_name in zip_files:
    # Construct the full path to the ZIP file
    zip_file_path = os.path.join(downloads_folder, zip_file_name)

    # Determine the name of the folder to extract to
    extracted_folder_name = os.path.splitext(zip_file_name)[0]
    extracted_folder_path = os.path.join(downloads_folder, extracted_folder_name)

    # Check if the specified ZIP file exists
    if os.path.isfile(zip_file_path) and zipfile.is_zipfile(zip_file_path):
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Create the extracted folder
            os.makedirs(extracted_folder_path, exist_ok=True)
            
            # Loop through each file in the zip file
            for file_info in zip_ref.infolist():
                # Check if it's a file and not inside a subfolder
                if file_info.is_dir() or os.path.dirname(file_info.filename):
                    continue

                # Extract only the top-level files to the new folder
                extracted_file_path = os.path.join(extracted_folder_path, os.path.basename(file_info.filename))
                with zip_ref.open(file_info.filename) as source, open(extracted_file_path, "wb") as target:
                    shutil.copyfileobj(source, target)
        
        # Move the extracted folder to the destination folder
        shutil.move(extracted_folder_path, os.path.join(destination_folder, extracted_folder_name))
        print(f"ZIP file '{zip_file_name}' has been extracted (top-level files only) to '{extracted_folder_name}' and moved successfully.")
    else:

        print(f"Error: The file '{zip_file_name}' does not exist or is not a valid ZIP file.")
