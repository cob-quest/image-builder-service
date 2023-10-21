import docker
import string, random
import zipfile, subprocess, os, time

from logger import logger
from bucket_connector import download_from_bucket
from db.crud_functions import CrudFunctions

# Connect to docker using default socket
client = docker.from_env()

# Retrieve container registry info from env
GITLAB_REGISTRY = os.getenv("GITLAB_REGISTRY")
GITLAB_USERNAME = os.getenv("GITLAB_USERNAME")
GITLAB_PASSWORD = os.getenv("GITLAB_PASSWORD")

# Login to Gitlab Container Registry
client.login(
    registry=GITLAB_REGISTRY,
    username=GITLAB_USERNAME,
    password=GITLAB_PASSWORD
)

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

def push_image(name_tag: str) -> None:
    '''
    Push docker image to Gitlab Container Registry
    
    Args: ``name_tag``(str) of the previously built image

    Returns: None
    '''
    logger.info(f"Pushing image {name_tag} to Gitlab Container Registry")

    try:
        resp = client.images.push(
            repository=f"{GITLAB_REGISTRY}/{name_tag}",
            stream=True
        )
        for line in resp:
            logger.debug(line)

        logger.info(f"Image pushed SUCCESS!")

    except Exception as e:
        raise ImagePushFailedException(str(e))


def build_image(image_name: str, creator_name: str) -> str:
    '''
    From the Dockerfile in image_to_build directory, build a docker image\n

    Args: ``image_name``(str) and ``creator_name``(str) as tag to the image

    Returns: ``id``(str)
    '''
    
    name_tag = create_name_tag(image_name, creator_name)

    logger.info(f"Building image {name_tag} from Dockerfile...")

    try:
        image_built = client.images.build(
            path='./image_to_build/',
            dockerfile='Dockerfile',
            tag=f"{GITLAB_REGISTRY}/{name_tag}",
            rm=True
        )
        logger.info(f"Image built SUCCESS | ID: {image_built[0].id}")
        return image_built[0].id, name_tag

    except Exception as e:
        raise ImageBuildFailedException(str(e))


def remove_image(image_id: str) -> None:
    '''
    This will be used upon the failure of pushing an image to registry.
    This is done for error handling, to remove the image.
    
    Args: ``image_id``(str)
    
    Returns: None
    '''

    retry_timer = 2

    while True:
        try:
            logger.info(f"Removing image: {image_id}")
            client.images.remove(image_id, force=True)
            logger.info(f"Remove image ({image_id}) SUCCESS!")
            return
            
        except docker.errors.ImageNotFound:
            logger.error(f"Image {image_id} not found.")
            return
            
        except docker.errors.APIError as e:
            logger.error(f"Error: {e}")
            logger.error(f"Removing image failed... Retrying in {retry_timer} seconds")
            time.sleep(retry_timer)
            retry_timer += 2


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
    if not message.get('fullPath', None):
        logger.error(f'Please specify full path to file to be downloaded!')
        return False

    # Depending on message, type, download files from S3 or clone from git
    try:
        download_from_bucket(message['fullPath'])
        extract_from_zip(message['fullPath'])
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
        id, name_tag = build_image(
            message['imageName'], 
            message['creatorName']
        )
        
        push_image(name_tag)

        # Write to DB
        DB.add_image(message)
        return True
    
    except ImageBuildFailedException as e:
        logger.error(e)
        
    except ImagePushFailedException as e:
        remove_image(id)
        logger.error(e)

    except Exception as e:
        logger.error(e)
        return False

    finally:
        # Clear image_to_build directory
        subprocess.run(["rm", "-rf", "image_to_build/"])
        subprocess.run(["mkdir", "image_to_build/"])
        logger.info("Cleared image_to_build directory")
