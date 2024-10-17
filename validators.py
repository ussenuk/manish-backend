# server/validators.py

import mimetypes

# Function to validate file types
def validate_file(file, allowed_types):
    if file:
        mime_type, _ = mimetypes.guess_type(file.filename)
        if not mime_type or mime_type not in allowed_types:
            return False
    return True

# Function to validate business description length
def validate_business_description(description):
    if len(description) < 200 or len(description) > 1000:
        return False
    return True