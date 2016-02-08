#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    05.02.2016 16:22:44 CET
# File:    __init__.py

from ._serializer_core import *
from . import _serializer_pickle
serializer.use('pickle')
