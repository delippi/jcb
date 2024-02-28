# --------------------------------------------------------------------------------------------------


import jcb
import os
import wxflow


# --------------------------------------------------------------------------------------------------


def abort_if(logger, condition, message):
    if condition:
        logger.error(message)
        raise ValueError(message)


# --------------------------------------------------------------------------------------------------


class Renderer():

    # ----------------------------------------------------------------------------------------------

    def __init__(self, dictionary_of_templates):

        # Create a logger
        self.logger = wxflow.Logger('Jedi Configuration Builder')

        # Write message showing that the Jedi Configuration Builder is being initialized
        self.logger.info('Initializing Jedi Configuration Builder')

        # Keep the dictionary of templates around
        self.dictionary_of_templates = dictionary_of_templates

        # Jedi dictionary to be returned
        self.jedi_dictionary = {}

        # Make sure the dictionary of templates has algorithm key
        abort_if(self.logger, 'algorithm' not in self.dictionary_of_templates,
                 'The dictionary of templates must have an algorithm key')

        # Path to configuration
        self.config_path = os.path.join(jcb.path(), 'configuration')

    # ----------------------------------------------------------------------------------------------

    def render(self):

        # This is where the rendering happens
        self.logger.info('Rendering JEDI configuration file')


# --------------------------------------------------------------------------------------------------


def render(dictionary_of_templates):

    # Create a jcb object
    jcb_object = Renderer(dictionary_of_templates)

    # Render the jcb object
    jcb_object.render()

    # Return the rendered jcb object
    return jcb_object.jedi_dictionary


# --------------------------------------------------------------------------------------------------
