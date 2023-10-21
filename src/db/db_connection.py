import os, time
import pymongo

from logger import logger
from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv('./secrets/.env')


MONGODB_HOSTNAME = os.getenv("MONGODB_HOSTNAME")
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_PORT = 27017

MONGOURI = f'mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOSTNAME}:{MONGODB_PORT}'
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
            db = client.get_database()
            image_collection = db['image_builder']

            # No duplcation of 'image_name' and 'image_ver' field
            image_collection.create_index("corId", unique=True)
            
            # image_collection.insert_one({
            #     "cor_id": "cor123",
            #     "creator_name": "cs302",
            #     "image_name": "first_image",
            #     "image_ver": "1.0",
            #     "container_url": "gitlab.com/first_image:1.0",
            #     "s3path": "github.com/s3/test"
            # })

            # image_collection.insert_one({
            #     "cor_id": "cor69",
            #     "creator_name": "cs302",
            #     "image_name": "second_image",
            #     "image_ver": "1.0",
            #     "container_url": "gitlab.com/first_image:1.0",
            #     "s3path": "github.com/s3/test"
            # })

            logger.info("Connected to MongoDB SUCCESS!")
            return image_collection
        
        except errors.ServerSelectionTimeoutError:
            logger.info(f"Failed to connect to MongoDB... Retrying in {retry_timer} seconds")
            time.sleep(retry_timer)
            retry_timer += 2
