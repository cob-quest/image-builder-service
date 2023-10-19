import os, time
import pymongo

from src.logger import logger
from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()

mongo_uri = os.getenv("MONGOURI")
client = MongoClient(mongo_uri)
    
def get_collection():
    """Get database connection

    Returns:
        Collection: A MongoClient collection
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
        
        except errors.ServerSelectionTimeoutError:
            logger.info(f"Failed to connect to MongoDB... Retrying in {retry_timer} seconds")
            time.sleep(retry_timer)
            retry_timer += 2
