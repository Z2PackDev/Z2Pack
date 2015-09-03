#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.09.2015 12:00:27 CEST
# File:    _result.py


class SurfaceResult(object):
    r"""
    Result class for surface calculations.
    """
    def __init__(self):
        # Think: which are 'essential', which derived -> keep essential ones only.
        self._t_points = []
        self._kpt_list = [] # what is this?
        self._gaps = []
        self._gapsize = []
        self._line_list = []
        # probably only keep _line_list and _t_points

class LineResult(object):
    r"""
    Result class for line calculations.
    """
    def __init__(self):
        self.wcc = None
        self.lambda_ = None
        self._converged = None
        self._max_move = None
        self._num_iter = None
