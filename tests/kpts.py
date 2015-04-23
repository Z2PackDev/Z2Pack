#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 12:20:27 CEST
# File:    kpts.py
"""Module containing the TestCase for Abinit k-point generation"""

from common import *
import numpy as np

class KptsAbinitTestCase(unittest.TestCase):
    """TestCase for the z2pack.fp.kpts.abinit function"""

    def test1_abinit(self):
        """test basic functionality (ABINIT)"""
        self.assertEqual(
            z2pack.fp.kpts.abinit(
                [[0.2, x, 0.5] for x in np.linspace(0, 1, 11)]),
            '\nkptopt -1\nndivk 9\nkptbounds 0.2 0.0 0.5 \n0.2 0.9 0.5 \n')

    def test2_abinit(self):
        """test basic functionality (ABINIT)"""
        self.assertEqual(
            z2pack.fp.kpts.abinit(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)]),
            '\nkptopt -1\nndivk 99\nkptbounds 0.0 0.6 0.5 \n0.99 0.6 0.5 \n')

    def test3_abinit(self):
        """test for ValueError with wrong dimension of point (ABINIT)"""
        self.assertRaises(
            ValueError,
            z2pack.fp.kpts.abinit,
            [[1, x] for x in np.linspace(0, 1, 10)])

    def test1_qe(self):
        """test basic functionality (Quantum Espresso)"""
        self.assertEqual(
            z2pack.fp.kpts.qe(
                [[0.2, x, 0.5] for x in np.linspace(0, 1, 11)]),
            '\nK_POINTS crystal_b\n 2 \n0.2 0.0 0.5 9\n0.2 0.9 0.5 1\n')

    def test2_qe(self):
        """test basic functionality (Quantum Espresso)"""
        self.assertEqual(
            z2pack.fp.kpts.qe(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)]),
            '\nK_POINTS crystal_b\n 2 \n0.0 0.6 0.5 99\n0.99 0.6 0.5 1\n')

    def test3_qe(self):
        """test for ValueError with wrong dimension of point (Quantum Espresso)"""
        self.assertRaises(
            ValueError,
            z2pack.fp.kpts.qe,
            [[1, x] for x in np.linspace(0, 1, 10)])

    def test1_wannier90(self):
        """test basic functionality (Wannier90)"""
        self.assertEqual(
            z2pack.fp.kpts.wannier90(
                [[0.2, x, 0.5] for x in np.linspace(0, 1, 11)]),
            'mp_grid: 10 1 1 \nbegin kpoints\n0.2 0.0 0.5 \n0.2 0.1 0.5 \n0.2 0.2 0.5 \n0.2 0.3 0.5 \n0.2 0.4 0.5 \n0.2 0.5 0.5 \n0.2 0.6 0.5 \n0.2 0.7 0.5 \n0.2 0.8 0.5 \n0.2 0.9 0.5 \nend kpoints\n')

    def test2_wannier90(self):
        """test basic functionality (Wannier90)"""
        self.assertEqual(
            z2pack.fp.kpts.wannier90(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)]),
            'mp_grid: 100 1 1 \nbegin kpoints\n0.0 0.6 0.5 \n0.01 0.6 0.5 \n0.02 0.6 0.5 \n0.03 0.6 0.5 \n0.04 0.6 0.5 \n0.05 0.6 0.5 \n0.06 0.6 0.5 \n0.07 0.6 0.5 \n0.08 0.6 0.5 \n0.09 0.6 0.5 \n0.1 0.6 0.5 \n0.11 0.6 0.5 \n0.12 0.6 0.5 \n0.13 0.6 0.5 \n0.14 0.6 0.5 \n0.15 0.6 0.5 \n0.16 0.6 0.5 \n0.17 0.6 0.5 \n0.18 0.6 0.5 \n0.19 0.6 0.5 \n0.2 0.6 0.5 \n0.21 0.6 0.5 \n0.22 0.6 0.5 \n0.23 0.6 0.5 \n0.24 0.6 0.5 \n0.25 0.6 0.5 \n0.26 0.6 0.5 \n0.27 0.6 0.5 \n0.28 0.6 0.5 \n0.29 0.6 0.5 \n0.3 0.6 0.5 \n0.31 0.6 0.5 \n0.32 0.6 0.5 \n0.33 0.6 0.5 \n0.34 0.6 0.5 \n0.35 0.6 0.5 \n0.36 0.6 0.5 \n0.37 0.6 0.5 \n0.38 0.6 0.5 \n0.39 0.6 0.5 \n0.4 0.6 0.5 \n0.41 0.6 0.5 \n0.42 0.6 0.5 \n0.43 0.6 0.5 \n0.44 0.6 0.5 \n0.45 0.6 0.5 \n0.46 0.6 0.5 \n0.47 0.6 0.5 \n0.48 0.6 0.5 \n0.49 0.6 0.5 \n0.5 0.6 0.5 \n0.51 0.6 0.5 \n0.52 0.6 0.5 \n0.53 0.6 0.5 \n0.54 0.6 0.5 \n0.55 0.6 0.5 \n0.56 0.6 0.5 \n0.57 0.6 0.5 \n0.58 0.6 0.5 \n0.59 0.6 0.5 \n0.6 0.6 0.5 \n0.61 0.6 0.5 \n0.62 0.6 0.5 \n0.63 0.6 0.5 \n0.64 0.6 0.5 \n0.65 0.6 0.5 \n0.66 0.6 0.5 \n0.67 0.6 0.5 \n0.68 0.6 0.5 \n0.69 0.6 0.5 \n0.7 0.6 0.5 \n0.71 0.6 0.5 \n0.72 0.6 0.5 \n0.73 0.6 0.5 \n0.74 0.6 0.5 \n0.75 0.6 0.5 \n0.76 0.6 0.5 \n0.77 0.6 0.5 \n0.78 0.6 0.5 \n0.79 0.6 0.5 \n0.8 0.6 0.5 \n0.81 0.6 0.5 \n0.82 0.6 0.5 \n0.83 0.6 0.5 \n0.84 0.6 0.5 \n0.85 0.6 0.5 \n0.86 0.6 0.5 \n0.87 0.6 0.5 \n0.88 0.6 0.5 \n0.89 0.6 0.5 \n0.9 0.6 0.5 \n0.91 0.6 0.5 \n0.92 0.6 0.5 \n0.93 0.6 0.5 \n0.94 0.6 0.5 \n0.95 0.6 0.5 \n0.96 0.6 0.5 \n0.97 0.6 0.5 \n0.98 0.6 0.5 \n0.99 0.6 0.5 \nend kpoints\n')

    def test3_wannier90(self):
        """test for ValueError with wrong dimension of point (Wannier90)"""
        self.assertRaises(
            ValueError,
            z2pack.fp.kpts.wannier90,
            [[1, x] for x in np.linspace(0, 1, 10)])

    def test1_vasp(self):
        """test basic functionality (VASP)"""
        self.assertEqual(
            z2pack.fp.kpts.vasp(
                [[0.2, x, 0.5] for x in np.linspace(0, 1, 11)]),
            'Automatic mesh\n0              ! number of k-points = 0 ->automatic generation scheme\nGamma          ! generate a Gamma centered grid\n1 10 1         ! subdivisions\n0.2 0.0 0.5          ! shift\n')

    def test2_vasp(self):
        """test basic functionality (VASP)"""
        self.assertEqual(
            z2pack.fp.kpts.vasp(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)]),
            'Automatic mesh\n0              ! number of k-points = 0 ->automatic generation scheme\nGamma          ! generate a Gamma centered grid\n100 1 1         ! subdivisions\n0.0 0.6 0.5          ! shift\n')

    def test3_vasp(self):
        """test for ValueError with wrong dimension of point (VASP)"""
        self.assertRaises(
            ValueError,
            z2pack.fp.kpts.vasp,
            [[1, x] for x in np.linspace(0, 1, 10)])

if __name__ == "__main__":
    unittest.main()
