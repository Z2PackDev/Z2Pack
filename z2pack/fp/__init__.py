#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
This specialisation of Z2Pack can handle systems computed with ab initio
codes interfacing to Wannier90.

.. note:: A modified version of Wannier90 is needed for Z2Pack. Please
    consult the :ref:`Tutorial<setup_first_principles>` for details.
"""

from ._first_principles import *
from . import kpoint

__all__ = ['kpoint'] + _first_principles.__all__  # pylint: disable=undefined-variable
