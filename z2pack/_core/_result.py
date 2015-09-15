#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.09.2015 12:00:27 CEST
# File:    _result.py

import copy

class SurfaceResult(object):
    r"""
    Result class for surface calculations.
    """
    def __init__(self):
        self._t_points = []
        self._lines = []

    def has_line(self, t):
        return t in self._t_points

    @property
    def result(self):
        return zip(self._t_points, self._lines)
    
    @property
    def num_lines(self):
        return len(self._t_points)
    
    def __getitem__(self, idx):
        return self._t_points[idx], self._lines[idx]

    def __setitem__(self, idx, line):
        self._lines[idx] = line

class LineResult(object):
    r"""
    Result class for line calculations.
    """
    def __init__(self):
        self.wcc = None
        self.gap = None
        self.gapsize = None
        self.lambda_ = None
        self.converged = None
        self.max_move = None
        self.num_iter = None

    @property
    def num_wcc(self):
        return len(self.wcc)

    def set(self, wcc, gap, gapsize, lambda_, converged, max_move, num_iter):
        self.wcc = wcc
        self.gap = gap
        self.gapsize = gapsize
        self.lambda_ = lambda_
        self.converged = converged
        self.max_move = max_move
        self.num_iter = num_iter

