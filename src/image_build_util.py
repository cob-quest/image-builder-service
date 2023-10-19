import docker
import zipfile, subprocess, os, time

from git import Repo
from logger import logger
from bucket_connector import download_from_bucket
from db.crud_functions import *

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

class ImageBuildFailedException(Exception):
    ...

class ImagePushFailedException(Exception):
    ...

def push_image(image_name: str, image_version: str) -> None:
    '''
    Push docker image to Gitlab Container Registry
    
    Args: ``image_name``(str) and ``image_version``(str) as tag to the image

    Returns: None
    '''
    logger.info(f"Pushing image {image_name}:{image_version} to Gitlab Container Registry")

    try:
        resp = client.images.push(
            repository=f"{GITLAB_REGISTRY}/{image_name}:{image_version}",
            stream=True
        )
        for line in resp:
            logger.debug(line)

        logger.info(f"Image pushed SUCCESS!")

    except Exception as e:
        raise ImagePushFailedException(str(e))


def build_image(image_name: str, image_version: str) -> str:
    '''
    From the Dockerfile in image_to_build directory, build a docker image\n

    Args: ``image_name``(str) and ``image_version``(str) as tag to the image

    Returns: ``id``(str)
    '''

    logger.info(f"Building image {image_name}:{image_version} from Dockerfile...")

    try:
        image_built = client.images.build(
            path='./image_to_build/',
            dockerfile='Dockerfile',
            tag=f"{GITLAB_REGISTRY}/{image_name}:{image_version}",
            rm=True
        )
        logger.info(f"Image built SUCCESS | ID: {image_built[0].id}")
        return image_built[0].id

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


def extract_from_zip(zip_filename: str) -> None:
    '''
    Extracts the contents of a zip file into the iamge_to_build directory\n

    Args: ``zip_filename``(str)

    Returns: ``None``
    '''

    logger.info("Extracting zip file containing Dockerfile...")

    try:
        with zipfile.ZipFile(f'./image_to_build/{zip_filename}', 'r') as zf:
            zf.extractall('./image_to_build/')
        logger.info(f"'{zip_filename}' extracted into image_to_build directory")

    except:
        logger.error(f"'{zip_filename}' not found in image_to_build directory")
        raise


def clone_from_git(git_link: str) -> None:
    '''(NOTE) This function is not for production use'''

    try:
        GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
        GITHUB_PAT = os.getenv("GITHUB_PAT")
        repo_url = f"https://{GITHUB_USERNAME}:{GITHUB_PAT}@{git_link.split('@')[1]}"
        repo = Repo.clone_from(repo_url, './image_to_build')
        logger.info(f"Cloned repo from Git | {repo}")

    except Exception as e:
        logger.error(e)
        raise


def set_up_image_to_build(message: dict) -> bool:
    
    # Check for invalid message type
    if message['type'] not in ['ZIP', 'GIT']:
        logger.error(f'Invalid message type of {message["type"]}, should be of value "ZIP" or "GIT')
        return False

    # Depending on message, type, download files from S3 or clone from git
    try:
        if message['type'] == 'ZIP':
            download_from_bucket(message['filename'])
            extract_from_zip(message['filename'])

        elif message['type'] == 'GIT':
            clone_from_git(message['link'])
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
        id = build_image(message['image_name'], message['image_ver'])
        
        push_image(message['image_name'], message['image_ver'])

        # Write to DB
        add_challenge(message)
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
