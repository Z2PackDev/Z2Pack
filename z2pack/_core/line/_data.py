#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 18:20:18 CET
# File:    _data.py

import numpy as np
import scipy.linalg as la

class LineData:
    def __init__(self, overlaps):
        self.overlaps = overlaps

    # Helpers for the automatically calculated attributes / properties
    _calculated_attrs = []

    def _property_helper(name_list, name):
        """Checks whether an attribute of the given name exists. If it does not, the decorated function is executed, which should produce the attribute. Finally, the attribute is returned."""
        name_list.append(name)
        def dec(f):
            def inner(self):
                if not hasattr(self, name):
                    f(self)
                return getattr(self, name)
            return inner
        return dec

    def __setattr__(self, key, value):
        if key == 'overlaps':
            for name in self.__class__._calculated_attrs:
                try:
                    delattr(self, name)
                except AttributeError:
                    pass
        super().__setattr__(key, value)

    @property
    @_property_helper(_calculated_attrs, '_lambda_')
    def lambda_(self):
        lambda_ = np.eye(len(self.overlaps[0]))
        for M in self.overlaps:
            [V, E, W] = la.svd(M)
            lambda_ = np.dot(np.dot(V, W).conjugate().transpose(), lambda_)
        self._lambda_ = lambda_

    @property
    @_property_helper(_calculated_attrs, '_wcc')
    def wcc(self):
        eigs, _ = la.eig(self.lambda_)
        self._wcc = sorted([(1j * np.log(z) / (2 * np.pi)).real % 1 for z in eigs])

    @property
    @_property_helper(_calculated_attrs, '_gap_pos')
    def gap_pos(self):
        self._calculate_gap()

    @property
    @_property_helper(_calculated_attrs, '_gap_size')
    def gap_size(self):
        self._calculate_gap()

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
