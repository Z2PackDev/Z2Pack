#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 16:04:23 CET
# File:    _data.py

import six
from ptools.locker import Locker
from sortedcontainers import SortedList

@six.add_metaclass(Locker)
class SurfaceData(object):
    def __init__(self):
        self.lines = SortedList(key=lambda x: x.t)

    def add(self, t, line_data):
        self.lines.add(SurfaceLine(t, line_data))

    @property
    def t(self):
        return tuple(line.t for line in self.lines)
    

@six.add_metaclass(Locker)
class SurfaceLine(object):
    def __init__(self, t, line_data):
        self.t = t
        self.line_data = line_data
