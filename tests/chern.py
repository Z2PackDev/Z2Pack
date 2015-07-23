#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    13.04.2015 16:52:29 CEST
# File:    chern.py

from common import *

import numpy as np

class ChernTestCase(CommonTestCase):

    def kp_hamilton(self, k):
        pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
        pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
        pauli_vector = list([pauli_x, pauli_y, pauli_z])
        k[2] = -k[2]
        res = np.zeros((2, 2), dtype=complex)
        for kval, p_mat in zip(k, pauli_vector):
            res += kval * p_mat
        return res

    def test_chern(self):
        system = z2pack.em.System(self.kp_hamilton)
        surface = system.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04), pickle_file=None)
        surface.wcc_calc(verbose=False)

        res = {'pol': [0.0, 0.97700105140316218, 0.90910824353141262, 0.80034213787699182, 0.65926687257349847, 0.5, 0.34073312742650147, 0.19965786212300812, 0.09089175646858734, 0.022998948596837845, 0.0], 'chern': -0.99999999999999989, 'step': [-0.02299894859683782, -0.067892807871749561, -0.1087661056544208, -0.14107526530349335, -0.15926687257349847, -0.15926687257349853, -0.14107526530349335, -0.10876610565442078, -0.067892807871749491, -0.022998948596837845]}

        self.assertFullAlmostEqual(res, surface.chern())

if __name__ == "__main__":
    unittest.main()    
