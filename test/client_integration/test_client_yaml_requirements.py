# --------------------------------------------------------------------------------------------------

import os

import jcb
import pytest
import re
import yaml


# --------------------------------------------------------------------------------------------------


def get_apps():

    # Get JCB path
    jcb_path = jcb.get_jcb_path()

    # Path to the apps
    apps_path = os.path.join(jcb_path, 'configuration', 'apps')

    # Return list of apps
    return [app for app in os.listdir(apps_path) if os.path.isdir(os.path.join(apps_path, app))]


# --------------------------------------------------------------------------------------------------

def get_list_of_yaml_files(app):

    yaml_files_dict = {}

    # Get JCB path
    jcb_path = jcb.get_jcb_path()

    # Path to the apps
    app_path = os.path.join(jcb_path, 'configuration', 'apps', app)

    # Get list of directories in the app_path
    app_dirs = [d for d in os.listdir(app_path) if os.path.isdir(os.path.join(app_path, d))]

    # Loop over the directories
    for app_dir in app_dirs:

        yaml_files_dict[app_dir] = []

        # Append with the yaml.j2 files in that directory
        for root, dirs, files in os.walk(os.path.join(app_path, app_dir)):
            for file in files:
                if file.endswith('.yaml.j2'):
                    yaml_files_dict[app_dir].append(file)

    return yaml_files_dict


# --------------------------------------------------------------------------------------------------


def test_check_for_yaml_anchors():

    print(get_apps())
    print(yaml.dump(get_list_of_yaml_files('gdas')))


# --------------------------------------------------------------------------------------------------

def test_client_allowable_components():

    # Get JCB path
    jcb_path = jcb.get_jcb_path()

    # List of apps is list of dirs in path_to_apps (e.g. gdas)
    apps = get_apps()

    # Optional directories for the application
    allowable_dirs = [
        'model',
        'observations',
        'algorithm',
        'observation_chronicle',
        ]

    # Loop over the apps
    for app in apps:

        # Path to the app
        app_path = os.path.join(jcb_path, 'configuration', 'apps', app)

        # Check that the directories within each app directory are allowable
        app_dirs = [d for d in os.listdir(app_path) if os.path.isdir(os.path.join(app_path, d))]

        # Check that all directories are allowable
        for d in app_dirs:
            assert d in allowable_dirs, f"Directory {d} is not allowable for app {app}."


# --------------------------------------------------------------------------------------------------


def test_client_model_is_prepended():

    # Get JCB path
    jcb_path = jcb.get_jcb_path()

    # List of apps is list of dirs in path_to_apps (e.g. gdas)
    apps = get_apps()

    # Loop over the apps
    for app in apps:

        # Path to the app
        app_model_path = os.path.join(jcb_path, 'configuration', 'apps', app, 'model')

        # Continue if no app_model_path
        if not os.path.exists(app_model_path):
            continue

        # List all the model components within the model directory
        model_components = os.listdir(app_model_path)

        # Loop over the model components
        for model_component in model_components:

            print(model_component)



# -------------------------------------------------------------------------------------------------


# Main entry point
if __name__ == "__main__":
    test_client_model_is_prepended() #pytest.main()


# --------------------------------------------------------------------------------------------------
