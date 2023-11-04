import os
import sys
import time

sys.path.append('./src')

from dotenv import load_dotenv
from logger import logger
from pymongo import ASCENDING, MongoClient, errors

load_dotenv('/app/secrets/.env')

MONGODB_HOSTNAME = os.getenv("MONGODB_HOSTNAME")
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_PORT = 27017

MONGOURI = f'mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOSTNAME}:{MONGODB_PORT}'
# MONGOURI = f'mongodb://{MONGODB_HOSTNAME}:{MONGODB_PORT}'

logger.info(MONGOURI)
client = MongoClient(MONGOURI)
    
def get_collection():
    """Get database connection

    Returns:
        Collection: A MongoClient collection
    """
    retry_timer = 2

    while True:
        try:
            logger.info("Connecting to MongoDB...")
            db = client.get_database("cob")
            image_collection = db['image_builder']

            # No duplcation of 'image_name' and 'image_ver' field
            # index = IndexModel([("corId",ASCENDING)])
            image_collection.create_index([("corId", ASCENDING)], unique=True)
            image_collection.create_index(
                [("creatorName", ASCENDING),
                ("imageName", ASCENDING),
                ("imageTag", ASCENDING)],
                unique=True
            )

            logger.info("Connected to MongoDB SUCCESS!")
            return image_collection

        except errors.ServerSelectionTimeoutError:
            logger.info(f"Failed to connect to MongoDB... Retrying in {retry_timer} seconds")
            time.sleep(retry_timer)
            retry_timer += 2