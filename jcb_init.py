# --------------------------------------------------------------------------------------------------


import os
import subprocess
import yaml


# --------------------------------------------------------------------------------------------------


def get_jcb_branch():

    # Command to get git branch
    git_branch_command = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']

    # Return current branch
    try:
        branch = subprocess.check_output(git_branch_command).strip().decode('utf-8')
        return branch if branch != 'HEAD' else None
    except subprocess.CalledProcessError:
        return None


# --------------------------------------------------------------------------------------------------


def branch_exists_on_remote(git_ls_remote_command):

    # Return status of branch existence
    try:
        subprocess.check_output(git_ls_remote_command)
        return True
    except subprocess.CalledProcessError:
        return False


# --------------------------------------------------------------------------------------------------


def update_default_branches(jcb_apps):

    # Get the current branch of the jcb repo
    jcb_branch = get_jcb_branch()

    # Nothing to do if the default branch is None or develop
    if jcb_branch is None or jcb_branch == 'develop':
        return

    # Loop over jcb_apps and update default branch
    for app, app_conf in jcb_apps.items():

        # Check if the default branch exists
        git_ls_remote_command = ['git', 'ls-remote', '--heads', app_conf['git_url'], jcb_branch]

        # If the branch exists, update the default branch
        if branch_exists_on_remote(git_ls_remote_command):
            app_conf['default_branch'] = jcb_branch


# --------------------------------------------------------------------------------------------------


def clone_or_update_repos(jcb_apps):

    # Loop over jcb_apps and clone or update the repositories
    for app, app_conf in jcb_apps.items():

        # Check if the target path exists
        if not os.path.exists(app_conf['target_path']):

            # Clone command
            git_clone = ['git', 'clone', app_conf['git_url'], '-b', app_conf['default_branch'],
                         app_conf['target_path']]

            # Clone the repository
            print(f"Cloning {app} with command: {' '.join(git_clone)}")
            subprocess.run(git_clone)


# --------------------------------------------------------------------------------------------------


if __name__ == "__main__":

    # Get the path of this file
    file_path = os.path.dirname(os.path.realpath(__file__))

    # Open the jcb_apps.yaml file
    with open(os.path.join(file_path, 'jcb_apps.yaml')) as file:
        jcb_apps = yaml.load(file, Loader=yaml.FullLoader)

    # Required keys
    required_keys = ['git_url', 'default_branch']

    # Set the path to where the applications will be cloned
    jcb_config_path = os.path.join(file_path, 'src', 'jcb', 'configuration')

    # Loop over jcb_apps and make sure required keys are present and add target_path
    for app, app_conf in jcb_apps.items():
        for key in required_keys:
            if key not in app_conf:
                raise Exception(f"Key '{key}' not found in jcb_apps.yaml")
        app_conf['target_path'] = os.path.join(jcb_config_path, 'apps', app)

    # Add jcb-algorithms to the dictionary
    jcb_apps['algorithms'] = {
        'git_url': 'https://github.com/noaa-emc/jcb-algorithms.git',
        'default_branch': 'develop',
        'target_path': os.path.join(jcb_config_path, 'algorithms')
    }

    # Get the current branch of the jcb repo
    update_default_branches(jcb_apps)

    # Clone or update the repositories
    clone_or_update_repos(jcb_apps)


# --------------------------------------------------------------------------------------------------
