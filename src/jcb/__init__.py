import os

# --------------------------------------------------------------------------------------------------

# Set the version
__version__ = '0.0.1'

# --------------------------------------------------------------------------------------------------

# Elevate all functions and classed to being useable as jcb.<function>
from .driver import main as jcb
from .renderer import Renderer as Renderer
from .renderer import render as render
from .observation_chronicle.observation_chronicle import *
from .observation_chronicle.satellite_chronicle import *
from .utilities.parse_channels import *
from .utilities.trapping import *

# --------------------------------------------------------------------------------------------------
