# --------------------------------------------------------------------------------------------------

import os

import jcb
import pytest
import yaml


# --------------------------------------------------------------------------------------------------


def test_jcb():

    # Load in dictionary of templates
    # -------------------------------
    dictionary_of_templates = os.path.join(os.path.dirname(__file__), 'gdas-templates.yaml')
    with open(dictionary_of_templates, 'r') as f:
        dictionary_of_templates = yaml.safe_load(f)

    # Style 1 for call: all in one API
    # --------------------------------

    jedi_dict_1 = jcb.render(dictionary_of_templates)

    print(yaml.dump(jedi_dict_1, default_flow_style=False, sort_keys=False))

    # Style 2 for call: renderer for multiple algorithms
    # --------------------------------------------------

    # Algorithm does not need to be in the dictionary of templates
    del dictionary_of_templates['algorithm']

    jcb_obj = jcb.Renderer(dictionary_of_templates)
    jedi_dict_2_a = jcb_obj.render('hofx4d')
    jedi_dict_2_b = jcb_obj.render('hofx4d')  # Same algo until we add more

    print(yaml.dump(jedi_dict_2_a, default_flow_style=False, sort_keys=False))
    print(yaml.dump(jedi_dict_2_b, default_flow_style=False, sort_keys=False))


# -------------------------------------------------------------------------------------------------


# Main entry point
if __name__ == "__main__":
    pytest.main()


# --------------------------------------------------------------------------------------------------
