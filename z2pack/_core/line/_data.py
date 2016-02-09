#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 18:20:18 CET
# File:    _data.py

import scipy.linalg as la

class LineData(object):
    def __init__(self, overlaps):
        self.overlaps = overlaps

    @property
    def lambda_(self):
        lambda_ = np.eye(len(self.overlaps[0]))
        if not hasattr(self, '_lambda_'):
            for M in self.overlaps:
                [V, E, W] = la.svd(M)
                lambda_ = np.dot(np.dot(V, W).conjugate().transpose(), lambda_)
        self._lambda_ = lambda_
        return self._lambda_

    @property
    def wcc(self):
        if not hasattr(self, '_wcc'):
            [eigs, _] = la.eig(self.lambda_)
            self._wcc = sorted([(1j * np.log(z) / (2 * np.pi)).real % 1 for z in eigs])
        return self._wcc

    @property
    def gap_pos(self):
        if not hasattr(self, '_gap_pos'):
            self._calculate_gap()
        return self._gap_pos

    @property
    def gap_size(self):
        if not hasattr(self, '_gap_size'):
            self._calculate_gap()
        return self._gap_size

    def _calculate_gap(self):
        gap_size = 0
        gap_idx = 0
        N = len(self.wcc)
        for i in range(0, N - 1):
            temp = self.wcc[i + 1] - self.wcc[i]
            if temp > gap_size:
                gap_size = temp
                gap_idx = i
        temp = self.wcc[0] - self.wcc[-1] + 1
        if temp > gap_size:
            gap_size = temp
            gap_idx = N - 1
        self._gap_pos = (self.wcc[gap_idx] + gap_size / 2)
        self._gap_size = gap_size
