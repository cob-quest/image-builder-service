import os
import sys
import subprocess

sys.path.append('/usr/image_builder/src')
from google.cloud import storage
from pathlib import Path
from dotenv import load_dotenv
from logger import logger

load_dotenv('/app/secrets/.env')

# Set up bucket parameters
BUCKET_NAME = os.getenv("BUCKET_NAME")
BUCKET_CREDS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
client = storage.Client.from_service_account_json(BUCKET_CREDS)
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
    base_filename = filename.split("/")[-1]

    try:
        # Check if image_to_build folder exists
        path_dir = Path('./image_to_build')
        if not path_dir.exists() or not path_dir.is_dir():
            logger.info("image_to_build/ directory does not exists, creating...")
            subprocess.run(['mkdir', 'image_to_build'])
            logger.info("image_to_build directory created!")

        else:
            logger.info("image_to_build directory already exists, downloading...")

        # Download the file
        blob = bucket.blob(filename)
        blob.download_to_filename(f'./image_to_build/{base_filename}')
        logger.info(f"Downloaded {base_filename} into image_to_build/ directory")

    except Exception as e:
        logger.error(e)
        raise


if __name__ == '__main__':
    # Upload a file for testing
    # upload_to_bucket('testing.zip')

    # Download a file for testing
    download_from_bucket('challenge-zips/jk-test-b311f71b-f9b2-4d71-bcfe-1a86fac9fa2d.zip')
