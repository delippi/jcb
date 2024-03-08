# --------------------------------------------------------------------------------------------------

import jcb
import jinja2
import os
import sys
import yaml

# --------------------------------------------------------------------------------------------------

class Renderer():

    """
    A class to render templates using Jinja2 based on a provided dictionary of templates.

    Attributes:
        template_dict (dict): A dictionary containing the templates and relevant paths.
        j2_search_paths (list): A list of paths where Jinja2 will look for template files.
    """

    def __init__(self, template_dict: dict):

        """
        Initializes the Renderer with a given template dictionary and sets up Jinja2 search paths.

        Args:
            template_dict (dict): A dictionary containing templates and their corresponding paths.
        """

        # Keep the dictionary of templates around
        self.template_dict = template_dict

        # Set the paths where jinja will look for files in the hierarchy
        # --------------------------------------------------------------
        # Set the config path
        config_path = os.path.join(os.path.dirname(__file__), 'configuration')

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

    def render(self, algorithm):

        """
        Renders a given algorithm.

        Args:
            algorithm (str): The name of the algorithm to assemble a YAML for.

        Returns:
            dict: The dictionary that can drive the JEDI executable.
        """

        # Create the Jinja2 environment
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.j2_search_paths),
                                 undefined=jinja2.StrictUndefined)

        # Load the algorithm template
        template = env.get_template(algorithm + '.yaml')

        # Render the template hierarchy
        try:
            jedi_dict_yaml = template.render(self.template_dict)
        except jinja2.exceptions.UndefinedError as e:
            print(f'Resolving templates for {algorithm} failed with the following exception: {e}')
            sys.exit(1)

        # Check that everything was rendered
        jcb.abort_if('{{' in jedi_dict_yaml, f'In template_string_jinja2 ' +
                     f'the output string still contains template directives. ' +
                     f'{jedi_dict_yaml}')

        jcb.abort_if('}}' in jedi_dict_yaml, f'In template_string_jinja2 ' +
                     f'the output string still contains template directives. ' +
                     f'{jedi_dict_yaml}')

        # Convert the rendered string to a dictionary
        return yaml.safe_load(jedi_dict_yaml)


# --------------------------------------------------------------------------------------------------


def render(template_dict: dict):

    """
    Creates JEDI executable using only a dictionary of templates.

    Args:
        template_dict (dict): A dictionary that must include an 'algorithm' key among the templates.

    Returns:
        dict: The rendered JEDI dictionary.

    Raises:
        Exception: If the 'algorithm' key is missing in the template dictionary.
    """

    # Create a jcb object
    jcb_object = Renderer(template_dict)

    # Make sure the dictionary of templates has the algorithm key
    jcb.abort_if('algorithm' not in template_dict,
                 'The dictionary of templates must have an algorithm key')

    # Extract algorithm from the dictionary of templates
    algorithm = template_dict['algorithm']

    # Render the jcb object
    return jcb_object.render(algorithm)


# --------------------------------------------------------------------------------------------------
