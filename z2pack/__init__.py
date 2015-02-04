#!/usr/bin/python3.3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    21.03.2014 11:46:38 CET
# File:    z2pack.py

"""
The core module contains the routines that are shared between different \
specialisations of Z2Pack (first-principles, tight-binding), and interfaces \
to those. It contains the classes System (which acts as hook for the \
specialisations) and Plane (responsible for all the calculations / \
plots etc.)
"""

from .core import *

from . import fp
from . import tb

