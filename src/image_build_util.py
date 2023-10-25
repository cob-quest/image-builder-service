import string, random
import zipfile, subprocess, os, time

from kaniko import Kaniko, KanikoSnapshotMode
from logger import logger
from bucket_connector import download_from_bucket
from src.config.crud_functions import CrudFunctions

# Create Kaniko instance
kaniko = Kaniko()

# Retrieve container registry info from env
GLREGISTRY = os.getenv("GLREGISTRY")
GLUSERNAME = os.getenv("GLUSERNAME")
GLTOKEN = os.getenv("GLTOKEN")

# Instantiate CRUD function instance
DB = CrudFunctions()

class ImageBuildFailedException(Exception):
    ...

class ImagePushFailedException(Exception):
    ...

def create_name_tag(image_name: str, creator_name: str) -> str:
    creator_name = creator_name.lower().replace(' ', '-')
    random_tag = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(4)])
    return f"{image_name}:{creator_name}-{random_tag}"


def build_image(image_name: str, creator_name: str) -> None:
    '''
    From the Dockerfile in image_to_build directory, build a docker image\n

    Args: ``image_name``(str) and ``creator_name``(str) as tag to the image

    Returns: ``id``(str)
    '''
    
    name_tag = create_name_tag(image_name, creator_name)

    logger.info(f"Building image {name_tag} from Dockerfile...")

    try:
        kaniko.force = True

        kaniko.build(
            docker_registry_uri=GLREGISTRY,
            registry_username=GLUSERNAME,
            registry_password=GLTOKEN,
            destination=f"{GLREGISTRY}/{name_tag}",
            dockerfile='./image_to_build/Dockerfile',
            context="/usr/image_builder/image_to_build",
            snapshot_mode=KanikoSnapshotMode.time
        )
        logger.info("Image built! Function finished running")
        return name_tag

    except Exception as e:
        raise ImageBuildFailedException(str(e))


def extract_from_zip(filename: str) -> None:
    '''
    Extracts the contents of a zip file into the iamge_to_build directory\n

    Args: ``filename``(str)

    Returns: ``None``
    '''

    logger.info("Extracting zip file containing Dockerfile...")
    
    base_filename = filename.split("/")[-1]

    try:
        with zipfile.ZipFile(f'./image_to_build/{base_filename}', 'r') as zf:
            zf.extractall('./image_to_build/')
        logger.info(f"'{base_filename}' extracted into image_to_build directory")

    except:
        logger.error(f"'{base_filename}' not found in image_to_build directory")
        raise


def set_up_image_to_build(message: dict) -> bool:
    
    # Check for invalid message type
    if not message.get('s3Path', None):
        logger.error(f'Please specify s3 path for file to be downloaded!')
        return False

    # Depending on message, type, download files from S3 or clone from git
    try:
        download_from_bucket(message['s3Path'])
        extract_from_zip(message['s3Path'])
        return True

    except:
        return False


def handle_message(message: dict) -> bool:
    '''
    Upon receiving a message from the queue,
    set up the image_to_build directory by downloading the files from
    GCS. Next, build the image and push it to the image registry.

    Args: ``message``(dict) format required:
            {
                image_name: name of image to build,
                image_ver: version of iamge,
                email: email of the image creator
            }

    Returns: ``status``(bool)
    '''
    
    # TODO: If image already exists in DB, exit

    # Set up image_to_build directory
    if not set_up_image_to_build(message):
        logger.info("Unable to set up image_to_build Directory... Exiting")
        return False

    try:
        name_tag = build_image(
            message['imageName'], 
            message['creatorName']
        )
        
        image_registry_link = f"{GLREGISTRY}/{name_tag}"
        message['imageRegistryLink'] = image_registry_link

        # Write to DB
        DB.add_image(message)
        return True
    
    except ImageBuildFailedException as e:
        logger.error(e)

    except Exception as e:
        logger.error(e)
        return False

    finally:
        # Clear image_to_build directory
        subprocess.run(["rm", "-rf", "image_to_build/"])
        subprocess.run(["mkdir", "image_to_build/"])
        logger.info("Cleared image_to_build directory")
