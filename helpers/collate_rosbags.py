import os
import shutil

# Define the source directory where you want to search for rosbag files.
source_directory = '/home/sush/klab2/rosbags'  # Replace with your source directory path.

# Define the destination directory where you want to copy the rosbag files.
destination_directory = '/home/sush/klab2/rosbags_collated/'  # Replace with your destination directory path.

# Walk through the source directory and its subdirectories.
for root, dirs, files in os.walk(source_directory):
    for folder in dirs:
        folder_path = os.path.join(root, folder)

        # List all files in the current folder.
        files_in_folder = os.listdir(folder_path)

        # Filter for rosbag files (you can modify the condition if needed).
        rosbag_files = [file for file in files_in_folder if file.endswith('.bag')]

        # Copy the rosbag files to the destination directory.
        for rosbag_file in rosbag_files:
            source_file_path = os.path.join(folder_path, rosbag_file)
            destination_file_path = os.path.join(destination_directory, rosbag_file)

            # Copy the file.
            shutil.copy(source_file_path, destination_file_path)
            print(f'Copied: {source_file_path} to {destination_file_path}')
