#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.09.2015 12:00:27 CEST
# File:    _result.py

from ptools.locker import ConstLocker

import six
import copy


@six.add_metaclass(ConstLocker)
class LineResult(object):
    r"""
    Result class for line calculations.
    """
    def __init__(self, wcc, gap, gapsize, lambda_, max_move, num_kpts, converged):
        self.wcc = wcc
        self.gap = gap
        self.gapsize = gapsize
        self.lambda_ = lambda_
        self.max_move = max_move
        self.num_kpts = num_kpts
        self.converged = converged

    @property
    def num_wcc(self):
        return len(self.wcc)
