from google_images_download import google_images_download
from PIL import Image
import os
import re

# Path to the error file
error_file_path = r"C:\Users\mikeg\Downloads\error.txt"

# Read the error file
with open(error_file_path, "r") as error_file:
    error_lines = error_file.readlines()

# Extract the image names, output folder, and format from the error lines
image_info = []
for line in error_lines:
    match = re.search(r"Texture Handler encountered missing texture file: (.+\.png|.+\.dds)", line)
    if match:
        image_path = match.group(1)
        if image_path.startswith("gfx/leaders"):
            image_info.append(image_path)

# Download and process each image
for image_path in image_info:
    # Extract the folder, filename, and format from the image path
    parts = image_path.split("/")
    folder = "/".join(parts[:-1])
    filename, format = os.path.splitext(parts[-1])

    # Download the image
    response = google_images_download.googleimagesdownload()
    arguments = {"keywords": filename, "limit": 1, "output_directory": "temp", "no_directory": True, "no_download": True}
    paths = response.download(arguments)

    # Get the first image URL
    first_image_url = paths[0][filename][0]

    # Process and save the image
    output_folder = os.path.join("gfx/leaders", folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    download_and_save_image(first_image_url, output_folder, filename + format)

print("Images downloaded, processed, and saved.")
