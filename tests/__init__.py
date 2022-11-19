import os
from dotenv import load_dotenv


def env_var_loader(file_name, file_path=None):
    """ Method that allows to load env variables in local from a file.
    Args:
        file_name: path to file with environment variables
        file_path: path to the file, if it is not provided it is assumed that the file is in the root of the project
        """
    if file_path:
        env_path = os.path.join(file_path, file_name)
    else:
        wd = os.getcwd()
        env_path = os.path.join(wd, file_name)

    if os.path.isfile(env_path):
        load_dotenv(dotenv_path=env_path)


env_var_loader('tests/.env')
