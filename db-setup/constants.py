import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
CLUSTER_NAME = os.getenv('CLUSTER_NAME')
DB_CONFIG = {
    'username': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'cluster_url': f'{CLUSTER_NAME}.z1l4e.mongodb.net'
}

# MongoDB URI Construction for Atlas
MONGO_URI = f"mongodb+srv://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['cluster_url']}/?retryWrites=true&w=majority&appName={CLUSTER_NAME}"

# Collection Names
COLLECTIONS = {
    'RESTAURANTS': 'restaurants',
    'AUDIT': 'audit',
    'USERS': 'users'
}

# Field Names
FIELDS = {
    'RESTAURANT': {
        'RESTAURANT_ID': 'restaurant_id',
        'NAME': 'name',
        'ADDRESS': 'address',
        'AVG_RATING': 'avg_rating',
        'CRITIC_REVIEWS': 'critic_reviews',
        'CREATED_AT': 'created_at',
        'UPDATED_AT': 'updated_at'
    },
    'AUDIT': {
        'KEY': 'key',
        'VALUE': 'value',
        'RESTAURANT_ID': 'restaurant_id',
        'ACTION_BY': 'action_by',
        'ACTION': 'action',
        'TIME_OF_ACTION': 'time_of_action'
    },
    'USER': {
        'NAME': 'name',
        'EMAIL': 'email',
        'PASSWORD': 'password',
        'CREATED_AT': 'created_at',
        'UPDATED_AT': 'updated_at'
    }
}

# Validation Schemas
JSON_SCHEMA_KEY = '$jsonSchema'
VALIDATION_SCHEMAS = {
    'restaurants': {
        'validator': {
            JSON_SCHEMA_KEY: {
                'bsonType': 'object',
                'required': ['name', 'address', 'avg_rating', 'critic_reviews'],
                'properties': {
                    'name': {'bsonType': 'string', 'minLength': 1},
                    'restaurant_id': {'bsonType': 'string'},
                    'address': {
                        'bsonType': 'object',
                        'required': ['building', 'coord', 'street', 'zipcode'],
                        'properties': {
                            'building': {'bsonType': 'string'},
                            'coord': {
                                'bsonType': 'array',
                                'minItems': 2,
                                'maxItems': 2,
                                'items': {'bsonType': 'double'}
                            },
                            'street': {'bsonType': 'string'},
                            'zipcode': {'bsonType': 'string', 'pattern': '^\d{5}$'}
                        }
                    },
                    'avg_rating': {'bsonType': 'double', 'minimum': 0, 'maximum': 5},
                    'critic_reviews': {
                        'bsonType': 'array',
                        'items': {
                            'bsonType': 'object',
                            'required': ['name', 'review', 'rating'],
                            'properties': {
                                'name': {'bsonType': 'string'},
                                'review': {'bsonType': 'string'},
                                'rating': {
                                    'bsonType': ['double', 'int'],  # Allow both double and integer
                                    'minimum': 0,
                                    'maximum': 5
                                },
                                'sentiment_score': {
                                    'bsonType': 'double',
                                    'minimum': -1,
                                    'maximum': 1
                                }
                            }
                        }
                    },
                    'created_at': {'bsonType': 'date'},
                    'updated_at': {'bsonType': 'date'}
                }
            }
        }
    },
    'audit': {
        'validator': {
            JSON_SCHEMA_KEY: {
                'bsonType': 'object',
                'required': ['key', 'value', 'restaurant_id', 'action_by', 'action', 'time_of_action'],
                'properties': {
                    'key': {'bsonType': 'string'},
                    'value': {'bsonType': ['object', 'string', 'array', 'double', 'int']},
                    'restaurant_id': {'bsonType': 'string'},
                    'action_by': {'bsonType': 'string'},
                    'action': {'enum': ['insert', 'update', 'delete']},
                    'time_of_action': {'bsonType': 'string'}
                }
            }
        }
    },
    'users': {
        'validator': {
            JSON_SCHEMA_KEY: {
                'bsonType': 'object',
                'required': ['name', 'email', 'password'],
                'properties': {
                    'name': {'bsonType': 'string'},
                    'email': {
                        'bsonType': 'string',
                        'pattern': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    },
                    'password': {'bsonType': 'string'},
                    'created_at': {'bsonType': 'date'},
                    'updated_at': {'bsonType': 'date'}
                }
            }
        }
    }
}

# File Paths
PATHS = {
    'RESTAURANT_DATA': 'data/restaurant_reviews.json',
    'AUDIT_DATA': 'data/audit_data.json',
    'USER_DATA': 'data/users.json'
}