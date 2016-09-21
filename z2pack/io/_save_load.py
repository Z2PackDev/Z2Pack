#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    21.09.2016 11:41:56 CEST
# File:    _save_load.py

from fsc.io_helper import SerializerDispatch

from . import _encoding

__all__ = ['save', 'load']

IO_HANDLER = SerializerDispatch(_encoding)

save = IO_HANDLER.save
load = IO_HANDLER.load
