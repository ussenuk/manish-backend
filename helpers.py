import os
from werkzeug.utils import secure_filename
import re

# Helper function to manually generate slugs without slugify
def generate_slug(title):
    # Replace spaces and non-alphanumeric characters with hyphens
    return re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()

def save_image(image, title):
    ext = image.filename.split('.')[-1]  # Get the file extension
    slug = generate_slug(title)  # Generate a slugified title manually
    file_name = f"{slug}.{ext}"  # Create the file name
    image_path = os.path.join('public/images/', secure_filename(file_name))  # Secure the file name and path

    # Ensure the directory exists before saving the image
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    
    image.save(image_path)  # Save the file
    return file_name
