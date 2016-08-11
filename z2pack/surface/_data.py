#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 16:04:23 CET
# File:    _data.py

from fsc.export import export
from fsc.locker import ConstLocker
from sortedcontainers import SortedList

@export
class SurfaceData(metaclass=ConstLocker):
    """
    Data container for a surface calculation. It contains the :class:`.LineResult` instances of all the lines on the surface which have been calculated.
    
    * ``wcc`` : A list of Wannier charge centers.
    * ``pol`` : The total polarization (sum of WCC) along the line.
    * ``gap_pos`` : The position of the largest gap between any two WCC.
    * ``gap_size``: The size of the largest gap between any two WCC.
    
    .. note::
        
        The WCC are given in reduced coordinates, which means the possible values range from 0 to 1. The same is true for all values derived from the WCC.
    
    """
    # cannot be pickled if it is a local method (lambda) in __init__
    # when python3.4 support is dropped, operator.attrgetter can be used
    @staticmethod
    def _sort_key(x):
        return x.t

    def __init__(self, lines=()):
        self.lines = SortedList(lines, key=self._sort_key)

    def add_line(self, t, result):
        self.lines.add(SurfaceLine(t, result))

    def __getattr__(self, key):
        if key != 'lines':
            return [getattr(line, key) for line in self.lines]
        raise AttributeError

    @property
    def t(self):
        return tuple(line.t for line in self.lines)

    def nearest_neighbour_dist(self, t):
        if len(self.t) == 0:
            return 1
        return min(abs(t - tval) for tval in self.t)

class SurfaceLine:
    __slots__ = ['t', 'result']

    def __init__(self, t, result):
        self.t = t
        self.result = result

    def __getattr__(self, key):
        if key not in ['t', 'result']:
            return getattr(self.result, key)
        return super().__getattribute__(key)
