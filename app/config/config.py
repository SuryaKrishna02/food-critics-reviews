import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Database Configuration
CLUSTER_NAME = os.getenv('CLUSTER_NAME')
DB_CONFIG = {
    'username': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'cluster_url': f'{CLUSTER_NAME}.z1l4e.mongodb.net',
}

# MongoDB URI Construction for Atlas
MONGODB_URI = f"mongodb+srv://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['cluster_url']}/?retryWrites=true&w=majority&appName={CLUSTER_NAME}"

# Initialize MongoDB connection
client = MongoClient(MONGODB_URI)
db = client["food-critic-reviews"]
users_collection = db["users"]
reviews_collection = db['restaurants']

# Get the Google Cloud Variables
LOCATION = os.getenv('LOCATION')
PROJECT_ID = os.getenv('PROJECT_ID')
BG_IMAGE_URL = os.getenv('BG_IMAGE_URL')