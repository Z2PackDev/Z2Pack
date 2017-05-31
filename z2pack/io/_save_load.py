#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fsc.iohelper import SerializerDispatch

from . import _encoding

__all__ = ['save', 'load']

IO_HANDLER = SerializerDispatch(_encoding)

save = IO_HANDLER.save
load = IO_HANDLER.load
