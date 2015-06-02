#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    13.04.2015 10:55:29 CEST
# File:    test_em.py


from common import *

import numpy as np
import warnings
#~ warnings.filterwarnings('ignore', category=DeprecationWarning)

pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
pauli_vector = list([pauli_x, pauli_y, pauli_z])

class TestEmTestCase(CommonTestCase):

    def tb_hamiltonian(self, k):
        k[2] = -k[2]
        res = np.zeros((2, 2), dtype=complex)
        for kval, p_mat in zip(k, pauli_vector):
            res += kval * p_mat
        return res

    def test_res_0(self):
        system = z2pack.em.System(self.tb_hamiltonian, pos=[[0, 0, 0], [0., 0., 0.]], occ=1)
        surface = system.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface.wcc_calc(pickle_file=None, verbose=False)

        res = in_place_replace(surface.get_res())
        self.assertFullAlmostEqual(surface.get_res(), res)

    def test_res_1(self):
        system = z2pack.em.System(self.tb_hamiltonian, pos=[[0.25, 0.25, 0.25], [0., 0., 0.]], occ=1)
        surface = system.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface.wcc_calc(pickle_file=None, verbose=False)

        res = in_place_replace(surface.get_res())
        self.assertFullAlmostEqual(surface.get_res(), res)
        
    def test_res_2(self):
        system = z2pack.em.System(self.tb_hamiltonian, pos=[[0.25, 0.25, 0.25], [0., 0., 0.]], occ=2)
        surface = system.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface.wcc_calc(pickle_file=None, verbose=False)

        res = in_place_replace(surface.get_res())
        self.assertFullAlmostEqual(surface.get_res(), res)
        
    def test_res_3(self):
        system1 = z2pack.em.System(self.tb_hamiltonian, pos=[[0.25, 0.25, 0.25], [0., 0., 0.]], occ=1)
        surface1 = system1.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface1.wcc_calc(pickle_file=None, verbose=False)

        system2 = z2pack.em.System(self.tb_hamiltonian, pos=[[0.25, 0.25, 0.25], [0., 0., 0.]])
        surface2 = system2.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface2.wcc_calc(pickle_file=None, verbose=False)

        self.assertFullAlmostEqual(surface1.get_res(), surface2.get_res())
        
    def test_res_4(self):
        system1 = z2pack.em.System(self.tb_hamiltonian, pos=[[0., 0., 0.], [0., 0., 0.]], occ=1)
        surface1 = system1.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface1.wcc_calc(pickle_file=None, verbose=False)

        system2 = z2pack.em.System(self.tb_hamiltonian, occ = 1)
        surface2 = system2.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface2.wcc_calc(pickle_file=None, verbose=False)

        self.assertFullAlmostEqual(surface1.get_res(), surface2.get_res())

    def test_error(self):
        self.assertRaises(ValueError, z2pack.em.System, lambda k: [[1]], occ=1, pos=[[0., 0., 0.], [0.5, 0.5, 0.5]])

if __name__ == "__main__":
    unittest.main()    
