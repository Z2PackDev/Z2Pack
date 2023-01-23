#!/usr/bin/env python
r"""
This specialisation of Z2Pack can handle systems computed with ab initio
codes interfacing to Wannier90.

.. note:: A modified version of Wannier90 is needed for Z2Pack. Please
    consult the :ref:`Tutorial<setup_first_principles>` for details.
"""

from . import kpoint
from ._first_principles import *

__all__ = ["kpoint"] + _first_principles.__all__  # pylint: disable=undefined-variable
