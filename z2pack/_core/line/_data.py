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

    @property
    @_property_helper('_lambda_')
    def lambda_(self):
        M_tot = np.eye(len(self.overlaps[0]))
        for M in self.overlaps:
            M_tot = np.dot(M_tot, M)
        [V, E, W] = la.svd(M_tot)
        lambda_ = np.dot(V, W)
        self._lambda_ = lambda_

    @property
    @_property_helper('_wcc')
    def wcc(self):
        self._calculate_wannier()
        return self._wcc
        
    @property
    @_property_helper('_wannier_vec')
    def wannier_vec(self):
        self._calculate_wannier()
    

    def _calculate_wannier(self):
        eigs, eigvec = la.eig(self.lambda_)
        wcc = np.array([(1j * np.log(z) / (2 * np.pi)).real % 1 for z in eigs])
        idx = np.argsort(wcc)

        self._wcc = list(wcc[idx])
        self._wannier_vec = list(eigvec.T[idx])

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
        N = len(self.eigenstates)
        #~ print(self.eigenstates[0].shape)
        eignum = len(self.eigenstates[0])
        eigsize = self.eigenstates[0][0].shape[0]

        for i in range(N - 1):
            Mnew = [
                [
                    sum(
                        np.conjugate(self.eigenstates[i][m][j]) * self.eigenstates[i + 1][n][j] 
                        for j in range(eigsize)
                    )
                    for n in range(eignum)
                ]
                for m in range(eignum)
            ]
            M.append(Mnew)
        self._overlaps = M
