# --------------------------------------------------------------------------------------------------

import configparser
import os
import sys

# --------------------------------------------------------------------------------------------------

def parse_submodules_return_local_path():

    # Path to submodule file
    file_path = os.path.dirname(os.path.realpath(__file__))
    git_modules_file = os.path.join(file_path, '.gitmodules')

    config = configparser.ConfigParser()
    config.read(git_modules_file)

    submodules = {}
    for section in config.sections():
        submodule_name = section.split('"')[1].lower()
        submodules[submodule_name] = {
            'path': config.get(section, 'path').lower(),
            'url': config.get(section, 'url').lower()
        }

    return submodules

# --------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    submodule_repo = sys.argv[1].lower()
    submodules_dict = parse_submodules_return_local_path()

    # Loop over submodules_dict
    for submodule_name, submodule in submodules_dict.items():
        print(submodule['url'], submodule_repo)
        if submodule['url'] == submodule_repo:
            repo_found = True
            # Export environment variable for path to repo
            print(submodule['path'])
            exit(0)

    # Fail if we got to here
    exit(1)

# --------------------------------------------------------------------------------------------------
