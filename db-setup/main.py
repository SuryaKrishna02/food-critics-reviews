import json
from pathlib import Path
from pymongo import MongoClient, ASCENDING, DESCENDING, GEOSPHERE
from typing import List, Dict, Any
from datetime import datetime, timezone
from pymongo.errors import BulkWriteError, ConnectionFailure, OperationFailure
from constants import (
    MONGO_URI, DB_CONFIG, COLLECTIONS, VALIDATION_SCHEMAS, 
    PATHS
)


class DatabaseConnectionError(Exception):
    """Exception raised for database connection issues"""
    pass

class DataValidationError(Exception):
    """Exception raised for data validation issues"""
    pass

class CollectionSetupError(Exception):
    """Exception raised for collection setup issues"""
    pass

class DataImportError(Exception):
    """Exception raised for data import issues"""
    pass

class DataVerificationError(Exception):
    """Exception raised for data verification issues"""
    pass

class RestaurantReviewsDB:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.client.admin.command('ping')
            self.db = self.client[DB_CONFIG['name']]
        except ConnectionFailure as e:
            raise DatabaseConnectionError(f"Failed to connect to MongoDB: {e}")
        except OperationFailure as e:
            raise DatabaseConnectionError(f"Database authentication failed: {e}")

    def __del__(self):
        if hasattr(self, 'client'):
            self.client.close()

    def _convert_to_float(self, value: Any) -> float:
        """Convert a value to float."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _process_coordinates(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """Process coordinates in address."""
        if 'coord' in address:
            address['coord'] = [self._convert_to_float(coord) for coord in address['coord']]
        return address

    def _process_review(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single review."""
        if 'rating' in review:
            review['rating'] = self._convert_to_float(review['rating'])
        if 'sentiment_score' in review:
            review['sentiment_score'] = self._convert_to_float(review['sentiment_score'])
        return review

    def _process_restaurant_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single restaurant document."""
        # Process avg_rating
        if 'avg_rating' in doc:
            doc['avg_rating'] = self._convert_to_float(doc['avg_rating'])
        
        # Process address
        if 'address' in doc:
            doc['address'] = self._process_coordinates(doc['address'])
        
        # Process reviews
        if 'critic_reviews' in doc:
            doc['critic_reviews'] = [self._process_review(review) for review in doc['critic_reviews']]
        
        return doc

    def _load_json_data(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load and parse JSON data from file."""
        with file_path.open('r', encoding='utf-8') as file:
            data = json.load(file)
            return data if isinstance(data, list) else [data]

    def read_json_file(self, file_path: str, collection_name: str) -> List[Dict[str, Any]]:
        """
        Read and process JSON file data.
        
        Args:
            file_path: Path to the JSON file
            collection_name: Name of the collection
            
        Returns:
            List of processed documents
        """
        try:
            path = Path(file_path)
            print(f"Reading data for {collection_name} from {file_path}")
            
            # Load data
            data_list = self._load_json_data(path)
            
            if not data_list:
                print(f"Warning: No data found in {file_path}")
                return []
            
            # Process data based on collection type
            if collection_name == COLLECTIONS['RESTAURANTS']:
                data_list = [self._process_restaurant_doc(doc) for doc in data_list]
            
            print(f"Successfully read {len(data_list)} records for {collection_name}")
            return data_list
            
        except FileNotFoundError:
            print(f"Error: Data file not found: {file_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in file {file_path}: {e}")
            return []
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            return []

    def create_collection_if_not_exists(self, collection_name: str) -> None:
        try:
            if collection_name not in self.db.list_collection_names():
                print(f"Creating collection: {collection_name}")
                self.db.create_collection(collection_name)
            
            if collection_name in VALIDATION_SCHEMAS:
                print(f"Applying validation schema to {collection_name}")
                self.db.command({
                    'collMod': collection_name,
                    **VALIDATION_SCHEMAS[collection_name]
                })
        except OperationFailure as e:
            print(f"Error creating collection {collection_name}: {e}")
            raise CollectionSetupError(f"Failed to create/modify collection {collection_name}: {e}")

    def create_indexes(self, collection_name: str) -> None:
        try:
            collection = self.db[collection_name]
            
            if collection_name == COLLECTIONS['RESTAURANTS']:
                # Create indexes for all relevant fields in restaurants collection
                indexes = [
                    # Primary identifier
                    [("restaurant_id", ASCENDING)],
                    
                    # Basic fields
                    [("name", ASCENDING)],
                    [("avg_rating", ASCENDING)],
                    
                    # Address fields - includes geospatial index
                    [("address.coord", GEOSPHERE)],
                    [("address.zipcode", ASCENDING)],
                    [("address.street", ASCENDING)],
                    [("address.building", ASCENDING)],
                    
                    # Critic reviews
                    [("critic_reviews.name", ASCENDING)],
                    [("critic_reviews.rating", ASCENDING)],
                    [("critic_reviews.review", ASCENDING)],
                    [("critic_reviews.sentiment_score", ASCENDING)],
                    
                    # Timestamps
                    [("created_at", DESCENDING)],
                    [("updated_at", DESCENDING)]
                ]
                
                print("Creating restaurant-specific indexes...")
                for index in indexes:
                    try:
                        print(f"Creating index on {index[0][0]}")
                        collection.create_index(index, background=True)
                    except Exception as e:
                        print(f"Error creating index {index}: {str(e)}")
                print("Restaurant indexes created successfully")
                    
            elif collection_name == COLLECTIONS['AUDIT']:
                # Create specific indexes for audit
                print("Creating audit-specific indexes...")
                collection.create_index([("restaurant_id", ASCENDING), ("time_of_action", DESCENDING)])
                collection.create_index([("action_by", ASCENDING)])
                collection.create_index([("action", ASCENDING)])
                print("Audit indexes created successfully")
                
            elif collection_name == COLLECTIONS['USERS']:
                # Create specific indexes for users
                print("Creating user-specific indexes...")
                collection.create_index([("email", ASCENDING)], unique=True)
                collection.create_index([("name", ASCENDING)])
                print("User indexes created successfully")
                
        except OperationFailure as e:
            print(f"Error creating indexes for {collection_name}: {e}")
            raise CollectionSetupError(f"Failed to create indexes for {collection_name}: {e}")

    def setup_collection(self, collection_name: str, data: List[Dict[str, Any]]) -> int:
        try:
            print(f"\nSetting up collection: {collection_name}")
            
            # Create collection and apply validation
            self.create_collection_if_not_exists(collection_name)
            
            # Create indexes
            self.create_indexes(collection_name)
            
            # Add timestamps if needed
            current_time = datetime.now(timezone.utc)
            for doc in data:
                doc['created_at'] = current_time
                doc['updated_at'] = current_time
            
            # Insert data
            if data:
                print(f"Inserting {len(data)} documents into {collection_name}")
                collection = self.db[collection_name]
                result = collection.insert_many(data, ordered=False)
                inserted_count = len(result.inserted_ids)
                print(f"Successfully inserted {inserted_count} documents into {collection_name}")
                return inserted_count
            else:
                print(f"No data to insert into {collection_name}")
                return 0
            
        except BulkWriteError as bwe:
            print(f"Bulk write error details: {bwe.details}")
            inserted_count = bwe.details.get('nInserted', 0)
            print(f"Partial success: Inserted {inserted_count} documents into {collection_name}")
            return inserted_count
        except Exception as e:
            print(f"Error in setup_collection for {collection_name}: {str(e)}")
            raise DataImportError(f"Failed to import data into {collection_name}: {str(e)}")

    def setup_database(self) -> Dict[str, int]:
        results = {}
        
        try:
            # Drop existing collections
            for collection_name in COLLECTIONS.values():
                if collection_name in self.db.list_collection_names():
                    print(f"Dropping existing collection: {collection_name}")
                    self.db[collection_name].drop()

            # Process restaurants first
            print("\nProcessing restaurants collection...")
            restaurant_data = self.read_json_file(PATHS['RESTAURANT_DATA'], COLLECTIONS['RESTAURANTS'])
            if restaurant_data:
                results[COLLECTIONS['RESTAURANTS']] = self.setup_collection(COLLECTIONS['RESTAURANTS'], restaurant_data)
            
            # Process audit data
            print("\nProcessing audit collection...")
            audit_data = self.read_json_file(PATHS['AUDIT_DATA'], COLLECTIONS['AUDIT'])
            if audit_data:
                results[COLLECTIONS['AUDIT']] = self.setup_collection(COLLECTIONS['AUDIT'], audit_data)
            
            # Process user data
            print("\nProcessing users collection...")
            user_data = self.read_json_file(PATHS['USER_DATA'], COLLECTIONS['USERS'])
            if user_data:
                results[COLLECTIONS['USERS']] = self.setup_collection(COLLECTIONS['USERS'], user_data)

            return results
            
        except Exception as e:
            print(f"Error during database setup: {str(e)}")
            return results

    def verify_data(self) -> Dict[str, Any]:
        try:
            print("\nVerifying data...")
            stats = {}
            
            # Verify restaurants
            if COLLECTIONS['RESTAURANTS'] in self.db.list_collection_names():
                restaurant_coll = self.db[COLLECTIONS['RESTAURANTS']]
                stats[COLLECTIONS['RESTAURANTS']] = {
                    'total_documents': restaurant_coll.count_documents({}),
                    'total_reviews': sum(len(doc.get('critic_reviews', [])) 
                                      for doc in restaurant_coll.find({}, {'critic_reviews': 1})),
                    'avg_restaurant_rating': restaurant_coll.aggregate([
                        {'$group': {'_id': None, 'avg': {'$avg': '$avg_rating'}}}
                    ]).next()['avg'] if restaurant_coll.count_documents({}) > 0 else 0
                }

            # Verify audit
            if COLLECTIONS['AUDIT'] in self.db.list_collection_names():
                audit_coll = self.db[COLLECTIONS['AUDIT']]
                stats[COLLECTIONS['AUDIT']] = {
                    'total_documents': audit_coll.count_documents({}),
                    'actions_breakdown': {
                        action: audit_coll.count_documents({'action': action})
                        for action in ['insert', 'update', 'delete']
                    }
                }

            # Verify users
            if COLLECTIONS['USERS'] in self.db.list_collection_names():
                user_coll = self.db[COLLECTIONS['USERS']]
                stats[COLLECTIONS['USERS']] = {
                    'total_users': user_coll.count_documents({}),
                    'unique_emails': len(user_coll.distinct('email'))
                }

            return stats
            
        except Exception as e:
            print(f"Error during data verification: {str(e)}")
            return {}

def main():
    try:
        # Initialize and setup database
        db_setup = RestaurantReviewsDB()
        print("Successfully connected to MongoDB Atlas!")
        
        # Setup database collections and get results
        results = db_setup.setup_database()
        print("\nDocuments inserted:")
        print(json.dumps(results, indent=2))
        
        # Verify and print statistics
        stats = db_setup.verify_data()
        print("\nDatabase Statistics:")
        print(json.dumps(stats, indent=2))
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        if 'db_setup' in locals():
            del db_setup

if __name__ == "__main__":
    main()