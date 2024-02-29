import jcb
import os

# --------------------------------------------------------------------------------------------------

# Set the version
__version__ = '0.0.1'

# --------------------------------------------------------------------------------------------------

# Clean imports for users
from .jcb import main as main
from .renderer import Renderer as Renderer
from .renderer import render as render
from .utils import *

# --------------------------------------------------------------------------------------------------
