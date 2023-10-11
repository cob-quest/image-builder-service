from dotenv import load_dotenv
import os
from . import DatabaseConnectionError
from pymongo import MongoClient, errors

load_dotenv()

mongo_uri = os.getenv("MONGOURI")
client = MongoClient(mongo_uri)
    
def get_db_collection():
    """Get the Database `challenges` which has a Collection `challenge`.

    Returns:
        Collection: A MongoClient collection

    Raises:
        DatabaseConnectionError: Connection error to database, and connection is not established
    """
    try:
        db = client.challenges
        challenge_collection = db['challenge']

        # No duplcation of 'image_url' field
        challenge_collection.create_index(['image_url'], unique=True)

        return challenge_collection
    except errors.ServerSelectionTimeoutError as e:
        raise DatabaseConnectionError(f'Error connecting to database: {str(e)}')