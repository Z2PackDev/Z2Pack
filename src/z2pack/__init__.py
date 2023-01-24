"""
The core module contains the routines that are shared between different specialisations of Z2Pack (first-principles, tight-binding, effective models), and interfaces to those.
"""

import importlib.metadata

__version__ = importlib.metadata.version(__name__.replace(".", "-"))

from . import _logging_format  # sets default logging levels / format
from . import fp, hm, invariant, io, line, plot, shape, surface, tb

__all__ = ["__version__", "line", "surface", "shape", "fp", "invariant", "plot"]
