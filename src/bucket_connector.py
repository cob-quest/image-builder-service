import os

from google.cloud import storage
from dotenv import load_dotenv
from logger import logger

load_dotenv()

# Set up bucket parameters
BUCKET_NAME = os.getenv("BUCKET_NAME")
client = storage.Client.from_service_account_json("./src/challenge-bucket-key.json")
bucket = client.bucket(BUCKET_NAME)

def upload_to_bucket(filename: str) -> None:
    try:
        blob = bucket.blob(filename)
        
        generation_match_precondition = 0
        blob.upload_from_filename(filename, if_generation_match=generation_match_precondition)
        logger.info(f"Uploaded {filename}")
    
    except Exception as e:
        logger.error(e)
        raise

def download_from_bucket(filename: str) -> None:
    try:
        blob = bucket.blob(filename)
        blob.download_to_filename(f'./image_to_build/{filename}')
        logger.info(f"Downloaded {filename} into image_to_build/ directory")
        
    except Exception as e:
        logger.error(e)
        raise


if __name__ == '__main__':
    # Upload a file for testing
    upload_to_bucket('testing.zip')
    
    # Download a file for testing
    download_from_bucket('testing.zip')