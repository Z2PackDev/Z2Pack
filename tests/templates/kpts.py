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
            in_place_replace(
                z2pack.fp.kpts.abinit(
                [[0.2, x, 0.5] for x in np.linspace(0, 1, 11)])))

    def test2_abinit(self):
        """test basic functionality (ABINIT)"""
        self.assertEqual(
            z2pack.fp.kpts.abinit(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)]),
            in_place_replace(
                z2pack.fp.kpts.abinit(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)])))

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
            in_place_replace(
                z2pack.fp.kpts.qe(
                [[0.2, x, 0.5] for x in np.linspace(0, 1, 11)])))

    def test2_qe(self):
        """test basic functionality (Quantum Espresso)"""
        self.assertEqual(
            z2pack.fp.kpts.qe(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)]),
            in_place_replace(
                z2pack.fp.kpts.qe(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)])))

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
            in_place_replace(
                z2pack.fp.kpts.wannier90(
                [[0.2, x, 0.5] for x in np.linspace(0, 1, 11)])))

    def test2_wannier90(self):
        """test basic functionality (Wannier90)"""
        self.assertEqual(
            z2pack.fp.kpts.wannier90(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)]),
            in_place_replace(
                z2pack.fp.kpts.wannier90(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)])))

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
            in_place_replace(
                z2pack.fp.kpts.vasp(
                [[0.2, x, 0.5] for x in np.linspace(0, 1, 11)])))

    def test2_vasp(self):
        """test basic functionality (VASP)"""
        self.assertEqual(
            z2pack.fp.kpts.vasp(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)]),
            in_place_replace(
                z2pack.fp.kpts.vasp(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)])))

    def test3_vasp(self):
        """test for ValueError with wrong dimension of point (VASP)"""
        self.assertRaises(
            ValueError,
            z2pack.fp.kpts.vasp,
            [[1, x] for x in np.linspace(0, 1, 10)])

if __name__ == "__main__":
    unittest.main()
