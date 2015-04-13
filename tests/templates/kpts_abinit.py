#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 12:20:27 CEST
# File:    kpts_abinit.py
"""Module containing the TestCase for Abinit k-point generation"""

from common import *
import numpy as np

class KptsAbinitTestCase(unittest.TestCase):
    """TestCase for the z2pack.fp.kpts.abinit function"""

    def test1(self):
        """test basic functionality"""
        self.assertEqual(
            z2pack.fp.kpts.abinit(
                [[0.2, x, 0.5] for x in np.linspace(0, 1, 11)]),
            in_place_replace(
                z2pack.fp.kpts.abinit(
                [[0.2, x, 0.5] for x in np.linspace(0, 1, 11)])))

    def test2(self):
        """test basic functionality"""
        self.assertEqual(
            z2pack.fp.kpts.abinit(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)]),
            in_place_replace(
                z2pack.fp.kpts.abinit(
                [[x, 0.6, 0.5] for x in np.linspace(0, 1, 101)])))

    def test3(self):
        """test for ValueError with wrong dimension of point"""
        self.assertRaises(
            ValueError,
            z2pack.fp.kpts.abinit,
            [[1, x] for x in np.linspace(0, 1, 10)])

if __name__ == "__main__":
    unittest.main()
