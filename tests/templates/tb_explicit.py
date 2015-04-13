#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    13.04.2015 10:55:29 CEST
# File:    tb_explicit.py


from common import *

import unittest
import numpy as np

pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
pauli_vector = list([pauli_x, pauli_y, pauli_z])

class TbExplicitHTestCase(CommonTestCase):

    def tb_hamiltonian(self, k):
        k[2] = -k[2]
        res = np.zeros((2, 2), dtype=complex)
        for kval, p_mat in zip(k, pauli_vector):
            res += kval * p_mat
        return res

    def test_explicitH(self):
        H1 = z2pack.tb.Hamilton()
        H1.add_atom(([0, 0], 1), [0, 0, 0])
        H1.create_hamiltonian()
        H1.hamiltonian = self.tb_hamiltonian
        system1 = z2pack.tb.System(H1)
        surface1 = system1.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface1.wcc_calc(pickle_file=None, verbose=False)

        H2 = z2pack.tb.Hamilton()
        H2.explicit_hamiltonian(self.tb_hamiltonian, occupied=1)
        system2 = z2pack.tb.System(H2)
        surface2 = system2.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface2.wcc_calc(pickle_file=None, verbose=False)

        self.assertDictAlmostEqual(surface1.get_res(), surface2.get_res())

    def test_explicitH_atoms(self):
        H1 = z2pack.tb.Hamilton()
        H1.add_atom(([0], 1), [0, 0, 0])
        H1.add_atom(([0], 0), [0.25, 0.25, 0.25])
        H1.create_hamiltonian()
        H1.hamiltonian = self.tb_hamiltonian
        system1 = z2pack.tb.System(H1)
        surface1 = system1.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface1.wcc_calc(pickle_file=None, verbose=False)

        H2 = z2pack.tb.Hamilton()
        H2.add_atom(([0], 1), [0, 0, 0])
        H2.add_atom(([0], 0), [0.25, 0.25, 0.25])
        H2.explicit_hamiltonian(self.tb_hamiltonian, atoms_at_origin=False)
        system2 = z2pack.tb.System(H2)
        surface2 = system2.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04))
        surface2.wcc_calc(pickle_file=None, verbose=False)

        self.assertDictAlmostEqual(surface1.get_res(), surface2.get_res())

    def test_error(self):
        H = z2pack.tb.Hamilton()
        H.add_atom(([0], 1), [0, 0, 0])
        self.assertRaises(ValueError, H.explicit_hamiltonian, self.tb_hamiltonian, atoms_at_origin=False, occupied=1)

        

if __name__ == "__main__":
    unittest.main()    
