#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    21.03.2014 11:46:38 CET
# File:    z2pack.py

"""
The core module contains the routines that are shared between different  specialisations of Z2Pack (first-principles, tight-binding), and interfaces  to those.

.. codeauthor:: Dominik Gresch <greschd@gmx.ch>
"""

from ._version import __version__

from . import line
from . import surface
from . import shapes

from . import fp
from . import em

import logging

from ._logging_tools import default_handler
logging.getLogger(__name__).setLevel(logging.INFO)
logging.getLogger(__name__).addHandler(default_handler)
