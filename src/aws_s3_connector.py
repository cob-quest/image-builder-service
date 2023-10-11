import boto3
from dotenv import load_dotenv
import os

from logger import logger

# Load env variables
load_dotenv()
S3_REGION = os.getenv("S3_REGION")

# Connect to S3
s3 = boto3.client('s3', region_name=S3_REGION)


def download_from_s3(filename: str) -> None:
    # Specify parameters regarding S3 side
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    OBJECT_KEY = f'uploaded/{filename}'

    # Specify local file path to save the file
    LOCAL_FILEPATH = f'./image_to_build/{filename}'

    try:
        # Download the file from S3 to local filepath
        s3.download_file(BUCKET_NAME, OBJECT_KEY, LOCAL_FILEPATH)
        logger.info(f"Downloaded {filename} into image_to_build/ directory")

    except Exception as e:
        logger.erorr(e)
        raise
