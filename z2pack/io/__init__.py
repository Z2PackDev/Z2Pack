#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    09.08.2016 16:45:38 CEST
# File:    __init__.py

"""This module contains functions for saving and loading Z2Pack objects."""

from . import _encoding
from fsc.io_helper import set_encoding as _set_encoding
from fsc.io_helper import save, load
_set_encoding(_encoding)
