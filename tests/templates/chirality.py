#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    12.04.2015 22:06:14 CEST
# File:    chirality.py

from common import *

import numpy as np

pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
pauli_vector = list([pauli_x, pauli_y, pauli_z])

class ChiralityTestCase(CommonTestCase):

    def test_positive(self):
        def tb_hamiltonian(k):
            res = np.zeros((2, 2), dtype=complex)
            for kval, p_mat in zip(k, pauli_vector):
                res += kval * p_mat
            return res
        H = z2pack.tb.Hamilton()
        H.add_atom(([0, 0], 1), [0, 0, 0])
        H.create_hamiltonian()
        H.hamiltonian = tb_hamiltonian
        system = z2pack.tb.System(H)
        surface = system.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.01))
        surface.wcc_calc(pickle_file=None, verbose=False)

        res = in_place_replace(surface.get_res())

        self.assertFullAlmostEqual(res, surface.get_res())

    def test_negative(self):
        def tb_hamiltonian(k):
            res = np.zeros((2, 2), dtype=complex)
            for kval, p_mat in zip([k[0], k[1], k[2]], pauli_vector):
                res += kval * p_mat
            return res
        H = z2pack.tb.Hamilton()
        H.add_atom(([0, 0], 1), [0, 0, 0])
        H.create_hamiltonian()
        H.hamiltonian = tb_hamiltonian
        system = z2pack.tb.System(H)
        surface = system.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface.wcc_calc(pickle_file=None, verbose=False)

        res = in_place_replace(surface.get_res())

        self.assertFullAlmostEqual(res, surface.get_res())


if __name__ == "__main__":
    unittest.main()    
