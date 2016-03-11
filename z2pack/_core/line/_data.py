#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 18:20:18 CET
# File:    _data.py

import numpy as np
import scipy.linalg as la

from .._utils import _gapfind
from .._helpers import _property_helper

class OverlapLineData:
    def __init__(self, overlaps):
        self._overlaps = overlaps

    @property
    def overlaps(self):
        return self._overlaps

    # old way
    #~ @property
    #~ @_property_helper('_lambda_')
    #~ def lambda_(self):
        #~ lambda_ = np.eye(len(self.overlaps[0]))
        #~ for M in self.overlaps:
            #~ [V, E, W] = la.svd(M)
            #~ lambda_ = np.dot(np.dot(V, W).conjugate().transpose(), lambda_)
        #~ self._lambda_ = lambda_

    # new way
    @property
    @_property_helper('_wilson')
    def wilson(self):
        self._wilson = np.eye(len(self.overlaps[0]))
        for M in self.overlaps:
            self._wilson = np.dot(self._wilson, M)

    @property
    @_property_helper('_wcc')
    def wcc(self):
        self._calculate_wannier()
        return self._wcc
        
    @property
    @_property_helper('_wilson_eigenstates')
    def wilson_eigenstates(self):
        self._calculate_wannier()
    

    def _calculate_wannier(self):
        eigs, eigvec = la.eig(self.wilson)
        wcc = np.array([np.angle(z) / (2 * np.pi) % 1 for z in eigs])
        idx = np.argsort(wcc)

        self._wcc = list(wcc[idx])
        self._wilson_eigenstates = list(eigvec.T[idx])

    @property
    @_property_helper('_wcc_sum')
    def pol(self):
        self._wcc_sum = sum(self.wcc) % 1

    @property
    @_property_helper('_gap_pos')
    def gap_pos(self):
        self._calculate_gap()

    @property
    @_property_helper('_gap_size')
    def gap_size(self):
        self._calculate_gap()

    def _calculate_gap(self):
        self._gap_pos, self._gap_size = _gapfind(self.wcc)

class EigenstateLineData(OverlapLineData):
    def __init__(self, eigenstates):
        self._eigenstates = eigenstates

    # Avoid direct access (setting) the eigenstates. Alternatively, one
    # could change __setattr__ to achieve the same.
    @property
    def eigenstates(self):
        return self._eigenstates
    
    @property
    @_property_helper('_overlaps')
    def overlaps(self):
        # create M - matrices
        
        M = []

        for i in range(len(self.eigenstates) - 1):
            M.append(np.dot(
                np.conjugate(self.eigenstates[i]),
                np.array(self.eigenstates[i + 1]).T
            ))
        self._overlaps = M
