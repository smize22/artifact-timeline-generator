import os
import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime

def format_timestamp(timestamp):
   """Format a timestamp into a readable date string."""
   return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def extract_metadata(image_path):
   """Extract metadata from an image file."""
   try:
       image = Image.open(image_path)
       metadata = {
           'Filename': os.path.basename(image_path),
           'Format': image.format,
           'Mode': image.mode,
           'Size': image.size,
           'Creation Date': format_timestamp(os.path.getctime(image_path)),
           'Modification Date': format_timestamp(os.path.getmtime(image_path)),
           'Exif Data': {}
       }

       # Attempt to extract EXIF data
       exif_data = image._getexif()
       if exif_data:
           for tag_id, value in exif_data.items():
               tag = TAGS.get(tag_id, tag_id)
               metadata['Exif Data'][tag] = value

       return metadata
   except Exception as e:
       print(f"Error extracting metadata from {image_path}: {e}")
       return None

def scan_directory(directory):
   """Scan the directory for image files and extract their metadata."""
   all_metadata = []

   for filename in os.listdir(directory):
       if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
           image_path = os.path.join(directory, filename)
           metadata = extract_metadata(image_path)
           if metadata:
               all_metadata.append(metadata)

   return all_metadata

def save_metadata_to_json(metadata, output_file):
   """Save extracted metadata to a JSON file."""
   with open(output_file, 'w') as json_file:
       json.dump(metadata, json_file, indent=4)

if __name__ == "__main__":
   # Specify the directory containing images
   directory = input("Enter the path to the directory containing images: ")

   # Scan the directory and extract metadata
   metadata_list = scan_directory(directory)

   # Print metadata and save it to a JSON file
   if metadata_list:
       for metadata in metadata_list:
           print(json.dumps(metadata, indent=4))

       # Save metadata to a JSON file
       output_file = os.path.join(directory, "image_metadata.json")
       save_metadata_to_json(metadata_list, output_file)
       print(f"Metadata saved to {output_file}")
   else:
       print("No images found in the specified directory.")
