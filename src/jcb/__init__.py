# --------------------------------------------------------------------------------------------------


# Set the version
__version__ = '0.0.1'


# --------------------------------------------------------------------------------------------------


# Elevate all functions and classed to being useable as jcb.<function>
# from .driver import main as jcb
from .observation_chronicle.observation_chronicle import ObservationChronicle
from .observation_chronicle.satellite_chronicle import process_satellite_chronicles
from .renderer import render as render
from .renderer import Renderer as Renderer
from .utilities.config_parsing import datetime_from_conf, duration_from_conf
from .utilities.parse_channels import parse_channels, parse_channels_set
from .utilities.trapping import abort, abort_if

# Define the
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
]


# --------------------------------------------------------------------------------------------------
