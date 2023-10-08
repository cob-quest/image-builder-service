############################################
## THIS FILE IS FOR TESTING PURPOSES ONLY ##
############################################


from git import Repo

def clone_from_git(git_link: str) -> None:
    try:
        return Repo.clone_from(git_link, './image_to_build/')
    
    except Exception as e:
        # logger.error(e)
        print(e)
        raise
    
if __name__ == '__main__':
    clone_from_git('https://github.com/hongyao38/cs302-test-repo.git')