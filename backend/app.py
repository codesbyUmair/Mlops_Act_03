from flask import Flask, request, jsonify, json
from flask_cors import CORS
from bson import ObjectId
import pymongo
from datetime import datetime
import os
import sys

app = Flask(__name__)
CORS(app)

# Add auto-reload support
app.config["DEBUG"] = True

# Get MongoDB URI from environment variable with fallback to mongodb container
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017/formdb')
print(f"Using MongoDB URI: {MONGODB_URI.split('@')[0].split('://')[0]}://*****@{MONGODB_URI.split('@')[-1] if '@' in MONGODB_URI else MONGODB_URI.split('://')[-1]}")

try:
    # Connect to MongoDB
    print("Attempting to connect to MongoDB...")
    client = pymongo.MongoClient(MONGODB_URI)
    # Verify connection works with a ping
    client.admin.command('ping')
    print("MongoDB connection successful!")
    db = client.get_database("formdb")
    submissions_collection = db.submissions
    db_connected = True
except Exception as e:
    print(f"MongoDB connection error: {e}", file=sys.stderr)
    db_connected = False

# Custom JSON encoder for MongoDB ObjectId and datetime
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for debugging connection issues"""
    return jsonify({
        "status": "ok",
        "mongodb_connected": db_connected,
        "mongodb_uri_set": bool(MONGODB_URI)
    })

@app.route('/api/submit', methods=['POST'])
def submit_form():
    if not db_connected:
        return jsonify({"error": "Database connection failed"}), 503
        
    content = request.json.get('content')
    
    if not content:
        return jsonify({"error": "Content is required"}), 400
        
    try:
        submission = {
            "content": content,
            "created_at": datetime.utcnow()
        }
        
        result = submissions_collection.insert_one(submission)
        submission_id = result.inserted_id
        
        return jsonify({
            "success": True,
            "message": "Form submitted successfully!",
            "id": str(submission_id)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    if not db_connected:
        return jsonify({"error": "Database connection failed"}), 503
        
    try:
        submissions = list(submissions_collection.find().sort("created_at", -1))
        
        return jsonify(submissions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Enable extra file watching for all Python files in the project
    extra_files = []
    for root, dirs, files in os.walk("."):
        for filename in files:
            if filename.endswith(".py"):
                extra_files.append(os.path.join(root, filename))
                
    app.run(host='0.0.0.0', port=5001, debug=True, extra_files=extra_files)