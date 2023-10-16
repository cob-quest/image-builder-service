from dotenv import load_dotenv
import os
from . import DatabaseConnectionError
from pymongo import MongoClient, errors
import pymongo

load_dotenv()

mongo_uri = os.getenv("MONGOURI")
client = MongoClient(mongo_uri)
    
def get_db_collection():
    """Get the Database `cs302` which has a Collection `challenge`.

    Returns:
        Collection: A MongoClient collection

    Raises:
        DatabaseConnectionError: Connection error to database, and connection is not established
    """
    try:
        db = client.cs302
        challenge_collection = db['challenge']

        # No duplcation of 'image_name' and 'image_ver' field
        challenge_collection.create_index([
            ('image_name', pymongo.ASCENDING),
            ('image_ver', pymongo.DESCENDING)
        ])

        return challenge_collection
    except errors.ServerSelectionTimeoutError as e:
        raise DatabaseConnectionError(f'Error connecting to database: {str(e)}')
