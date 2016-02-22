#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 16:04:23 CET
# File:    _data.py

from ...ptools.locker import Locker
from sortedcontainers import SortedList

class SurfaceData(metaclass=Locker):
    def __init__(self):
        self.lines = SortedList(key=lambda x: x.t)

    def add_line(self, t, result):
        self.lines.add(SurfaceLine(t, result))

    @property
    def t(self):
        return tuple(line.t for line in self.lines)

    def nearest_neighbour_dist(self, t):
        if len(self.t) == 0:
            return 1
        return min(abs(t - tval) for tval in self.t)

class SurfaceLine(metaclass=Locker):
    def __init__(self, t, result):
        self.t = t
        self.result = result
