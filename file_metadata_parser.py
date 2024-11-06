from PIL import Image, ExifTags
import os
import hashlib
import json
import datetime

# Function to convert IFDRational to float
def rational_to_float(rational):
    if isinstance(rational, tuple) and len(rational) == 2:
        return rational[0] / rational[1]
    return rational

# Function to handle non-serializable EXIF data
def serialize_exif_data(exif_data):
    serialized_data = {}
    for key, value in exif_data.items():
        try:
            # Convert IFDRational to float
            if isinstance(value, tuple) and len(value) == 2:  # IFDRational
                serialized_data[key] = rational_to_float(value)
            else:
                serialized_data[key] = value if isinstance(value, (int, str, float, bool)) else str(value)
        except Exception as e:
            # In case there is an issue with conversion, log the error and skip the problematic field
            serialized_data[key] = f"Error: {e}"
    return serialized_data

# Function to extract GPS metadata
def extract_gps_data(exif_data):
    gps_info = {}
    if 'GPSInfo' in exif_data:
        gps_data = exif_data['GPSInfo']
        gps_info['Latitude'] = rational_to_float(gps_data[2])
        gps_info['Longitude'] = rational_to_float(gps_data[4])
    return gps_info

# Function to calculate file hashes (MD5 and SHA256)
def calculate_file_hashes(file_path):
    hash_md5 = hashlib.md5()
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hash_md5.update(chunk)
            hash_sha256.update(chunk)
    return hash_md5.hexdigest(), hash_sha256.hexdigest()

# Function to convert Unix timestamp to human-readable format
def unix_to_readable(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Main code
directory = input("Enter the path to the directory containing images: ")
print(f"Scanning directory: {directory}")

metadata_list = []

for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        try:
            print(f"Processing image: {file_path}")
            image = Image.open(file_path)
           
            # Check for EXIF data and handle if absent
            exif_data = {}
            if hasattr(image, '_getexif') and image._getexif():
                exif_data = {
                    ExifTags.TAGS.get(k, k): v
                    for k, v in image._getexif().items()
                    if k in ExifTags.TAGS
                }
            else:
                print(f"No EXIF data found for {file_path}")

            # Serialize EXIF data to handle non-serializable types
            exif_data = serialize_exif_data(exif_data)

            # Extract basic metadata
            metadata = {
                'Filename': filename,
                'Format': image.format,
                'Mode': image.mode,
                'Size': image.size,
                'Creation Date': unix_to_readable(os.path.getctime(file_path)),  # Convert to human-readable format
                'Modification Date': unix_to_readable(os.path.getmtime(file_path)),  # Convert to human-readable format
                'Exif Data': exif_data
            }
           
            # Add GPS data if available
            gps_data = extract_gps_data(exif_data)
            if gps_data:
                metadata['GPS Data'] = gps_data

            # Add file hashes
            md5_hash, sha256_hash = calculate_file_hashes(file_path)
            metadata['MD5 Hash'] = md5_hash
            metadata['SHA256 Hash'] = sha256_hash

            metadata_list.append(metadata)
       
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")

# Output metadata to JSON
try:
    print(json.dumps(metadata_list, indent=4))
except TypeError as e:
    print(f"Error serializing metadata to JSON: {e}")
