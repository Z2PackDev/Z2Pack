#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    13.04.2015 16:52:29 CEST
# File:    chern.py

from common import *

import numpy as np

class ChernTestCase(CommonTestCase):

    def tb_hamiltonian(self, k):
        pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
        pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
        pauli_vector = list([pauli_x, pauli_y, pauli_z])
        res = np.zeros((2, 2), dtype=complex)
        for kval, p_mat in zip([k[0], k[1], -k[2]], pauli_vector):
            res += kval * p_mat
        return res

    def test_chern(self):
        H = z2pack.tb.Hamilton()
        H.explicit_hamiltonian(self.tb_hamiltonian, occupied=1)
        system = z2pack.tb.System(H)
        surface = system.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface.wcc_calc(pickle_file=None, verbose=False)

        res = in_place_replace(surface.chern())

        self.assertFullAlmostEqual(res, surface.chern())

if __name__ == "__main__":
    unittest.main()    
