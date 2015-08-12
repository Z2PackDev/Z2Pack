#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    27.01.2015 12:01:28 CET
# File:    __init__.py

r"""
This specialisation of Z2Pack can handle systems computed with ab initio
codes interfacing to Wannier90.

.. note:: A modified version of Wannier90 is needed for Z2Pack. Please
    consult the :ref:`Tutorial<Wannier90_setup>` for details.
"""

from ._first_principles import *

