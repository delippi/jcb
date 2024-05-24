# --------------------------------------------------------------------------------------------------


import os

from .observation_chronicle.observation_chronicle import ObservationChronicle
from .observation_chronicle.satellite_chronicle import process_satellite_chronicles
from .renderer import render as render
from .renderer import Renderer as Renderer
from .utilities.config_parsing import datetime_from_conf, duration_from_conf
from .utilities.parse_channels import parse_channels, parse_channels_set
from .utilities.trapping import abort, abort_if


# --------------------------------------------------------------------------------------------------


# Set the JCB version
def version():
    return '0.0.1'


# --------------------------------------------------------------------------------------------------


# Define the visible functions and classes
__all__ = [
    'Renderer',
    'render',
    'ObservationChronicle',
    'process_satellite_chronicles',
    'datetime_from_conf',
    'duration_from_conf',
    'parse_channels',
    'parse_channels_set',
    'abort_if',
    'abort',
    'version',
    'get_jcb_path',
]


# --------------------------------------------------------------------------------------------------


# Function that returns the path of the this file
def get_jcb_path():
    return os.path.dirname(os.path.realpath(__file__))


# --------------------------------------------------------------------------------------------------
