import os
import json
from PIL import Image, ExifTags
import hashlib

# Helper functions
def get_decimal_from_dms(dms, ref):
    # ...

def extract_gps_data(exif_data):
    # ...

def calculate_file_hashes(filepath):
    # ...

# Main script
directory = input("Enter the path to the directory containing images: ")
metadata_list = []

for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    try:
        with Image.open(filepath) as img:
            metadata = {
                "Filename": filename,
                "Format": img.format,
                "Mode": img.mode,
                "Size": img.size,
                "Creation Date": os.path.getctime(filepath),
                "Modification Date": os.path.getmtime(filepath)
            }

            # Extract EXIF data
            exif_data = img._getexif()
            if exif_data:
                metadata["Exif Data"] = {}
                for tag, value in exif_data.items():
                    decoded = ExifTags.TAGS.get(tag, tag)
                    if decoded == "GPSInfo":
                        gps_data = extract_gps_data(exif_data)
                        if gps_data:
                            metadata["Exif Data"]["GPS Info"] = gps_data
                    else:
                        metadata["Exif Data"][decoded] = value

            # Add file hashes
            metadata["Hashes"] = calculate_file_hashes(filepath)

            # Add metadata to list
            metadata_list.append(metadata)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

print(json.dumps(metadata_list, indent=4))
