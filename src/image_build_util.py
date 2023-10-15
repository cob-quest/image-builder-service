import docker
import zipfile, subprocess, os

from git import Repo
from logger import logger
from aws_s3_connector import download_from_s3

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


def push_image(image_name: str, image_version: str):
    logger.info(f"Pushing image {image_name}:{image_version} to Gitlab Container Registry")
    
    resp = client.images.push(
        repository=f"{GITLAB_REGISTRY}/{image_name}:{image_version}",
        stream=True
    )
    
    for line in resp:
        logger.debug(line)


def build_image(image_name: str, image_version: str):
    '''
    From the Dockerfile in image_to_build directory, build a docker image\n
    
    Args: ``image_name``(str) and ``image_version``(str) as tag to the image

    Returns: The newly build ``image``(Image)
    '''
    
    logger.info(f"Building image {image_name}:{image_version} from Dockerfile...")
    
    return client.images.build(
        path='./image_to_build/',
        dockerfile='Dockerfile',
        tag=f"{GITLAB_REGISTRY}/{image_name}:{image_version}",
        rm=True
    )


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
            download_from_s3(message['filename'])
            extract_from_zip(message['filename'])
            
        elif message['type'] == 'GIT':
            clone_from_git(message['link'])
        return True
    
    except:
        return False


def handle_message(message: dict) -> None:
    
    # Set up image_to_build directory
    if not set_up_image_to_build(message):
        logger.info("Unable to set up image_to_build Directory... Exiting")
        return False
    
    try:
        # Build image
        image_built = build_image(message['image_name'], message['image_ver'])
        logger.info(f"Image built SUCCESS: {image_built}")
        
        # Push image
        image_pushed = push_image(message['image_name'], message['image_ver'])
        logger.info(f"Image pushed SUCCESS: {image_pushed}")
        return True
    
    except Exception as e:
        logger.error(e)
        return False
    
    finally:
        # Clear image_to_build directory
        subprocess.run(["rm", "-rf", "image_to_build/"])
        subprocess.run(["mkdir", "image_to_build/"])
        logger.info("Cleared image_to_build directory")

