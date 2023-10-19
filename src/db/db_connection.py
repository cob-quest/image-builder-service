import os, time
import pymongo

from logger import logger
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from db.DatabaseConnectionError import DatabaseConnectionError

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
    retry_timer = 2
    
    while True:
        try:
            logger.info("Connecting to MongoDB...")
            db = client.get_database()
            challenge_collection = db['challenge']

            # No duplcation of 'image_name' and 'image_ver' field
            challenge_collection.create_index([
                ('image_name', pymongo.ASCENDING),
                ('image_ver', pymongo.DESCENDING)
            ])

            logger.info("Connected to MongoDB SUCCESS!")
            return challenge_collection
        
        except errors.ServerSelectionTimeoutError as e:
            # raise DatabaseConnectionError(f'Error connecting to database: {str(e)}')
            logger.info(f"Failed to connect to MongoDB... Retrying in {retry_timer} seconds")
            time.sleep(retry_timer)
            retry_timer += 2
