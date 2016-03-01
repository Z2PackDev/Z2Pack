#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 18:20:18 CET
# File:    _data.py

import numpy as np
import scipy.linalg as la

from .._utils import _gapfind

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

    #~ @property
    #~ @_property_helper(_calculated_attrs, '_lambda_')
    #~ def lambda_(self):
        #~ lambda_ = np.eye(len(self.overlaps[0]))
        #~ for M in self.overlaps:
            #~ [V, E, W] = la.svd(M)
            #~ lambda_ = np.dot(np.dot(V, W).conjugate().transpose(), lambda_)
        #~ self._lambda_ = lambda_

    @property
    @_property_helper(_calculated_attrs, '_lambda_')
    def lambda_(self):
        M_tot = np.eye(len(self.overlaps[0]))
        for M in self.overlaps:
            M_tot = np.dot(M_tot, M)
        [V, E, W] = la.svd(M_tot)
        lambda_ = np.dot(V, W)
        self._lambda_ = lambda_

    @property
    @_property_helper(_calculated_attrs, '_wcc')
    def wcc(self):
        eigs, eigvecs = la.eig(self.lambda_)
        print(eigvecs)
        self._wcc = sorted([(1j * np.log(z) / (2 * np.pi)).real % 1 for z in eigs])

    @property
    @_property_helper(_calculated_attrs, '_wcc_sum')
    def pol(self):
        self._wcc_sum = sum(self.wcc) % 1

    @property
    @_property_helper(_calculated_attrs, '_gap_pos')
    def gap_pos(self):
        self._calculate_gap()

    @property
    @_property_helper(_calculated_attrs, '_gap_size')
    def gap_size(self):
        self._calculate_gap()

    def _calculate_gap(self):
        self._gap_pos, self._gap_size = _gapfind(self.wcc)
