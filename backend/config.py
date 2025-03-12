import os

# Get MongoDB URI from environment variable
# If not provided, use a default value for testing
MONGODB_URI = os.environ.get('MONGODB_URI')

# If MONGODB_URI is not provided or empty, use this fallback for local development
if not MONGODB_URI:
    print("Warning: No MongoDB URI provided. Using a fallback connection.")
    MONGODB_URI = "mongodb://localhost:27017/formdb"