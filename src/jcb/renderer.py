# --------------------------------------------------------------------------------------------------


import jcb
import jinja2
import os
import yaml


# --------------------------------------------------------------------------------------------------


def abort_if(condition: bool, message: str):
    if condition:
        print("\033[31m" + message + "\033[0m")
        raise ValueError(message)


# --------------------------------------------------------------------------------------------------


class Renderer():

    # ----------------------------------------------------------------------------------------------

    def __init__(self, template_dict: dict):

        # Keep the dictionary of templates around
        self.template_dict = template_dict

        # Make sure the dictionary of templates has the algorithm key
        abort_if('algorithm' not in self.template_dict,
                 'The dictionary of templates must have an algorithm key')

        # Set the paths where jinja will look for files in the hierarchy
        # --------------------------------------------------------------
        # Set the config path
        config_path = os.path.join(jcb.path(), 'configuration')

        # Path with the algorithm files (top level templates)
        self.j2_search_paths = [os.path.join(config_path, 'algorithms')]

        # Path with model files if app needs model things
        if 'app_path_model' in self.template_dict:
            self.j2_search_paths += [os.path.join(config_path, 'apps',
                                             self.template_dict['app_path_model'], 'model')]

        # Path with observation files if app needs obs things
        if 'app_path_observations' in self.template_dict:
            self.j2_search_paths += [os.path.join(config_path, 'apps',
                                             self.template_dict['app_path_observations'],
                                             'observations')]

    # ----------------------------------------------------------------------------------------------

    def render(self):

        # Create the Jinja2 environment
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.j2_search_paths))

        # Load the algorithm template
        template = env.get_template(self.template_dict['algorithm'] + '.yaml')

        # Render the template hierarchy
        return template.render(self.template_dict)


# --------------------------------------------------------------------------------------------------


def render(template_dict: dict):

    # Create a jcb object
    jcb_object = Renderer(template_dict)

    # Render the jcb object
    jedi_dict_str = jcb_object.render()

    # Convert the rendered string to a dictionary
    return yaml.safe_load(jedi_dict_str)


# --------------------------------------------------------------------------------------------------
