#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 10:22:43 CEST
# File:    tb_example.py

from common import *

import os
import types
import shutil

class TbExampleTestCase(BuildDirTestCase):

    def createH(self, t1, t2):

        self.H = z2pack.tb.Hamilton()

        # create the two atoms
        self.H.add_atom(([1, 1], 1), [0, 0, 0])
        self.H.add_atom(([-1, -1], 1), [0.5, 0.5, 0])

        # add hopping between different atoms
        self.H.add_hopping(((0, 0), (1, 1)),
                           z2pack.tb.vectors.combine([0, -1], [0, -1], 0),
                           t1,
                           phase=[1, -1j, 1j, -1])
        self.H.add_hopping(((0, 1), (1, 0)),
                           z2pack.tb.vectors.combine([0, -1], [0, -1], 0),
                           t1,
                           phase=[1, 1j, -1j, -1])

        # add hopping between neighbouring orbitals of the same type
        self.H.add_hopping((((0, 0), (0, 0)), ((0, 1), (0, 1))),
                           z2pack.tb.vectors.neighbours([0, 1],
                                                        forward_only=True),
                           t2,
                           phase=[1])
        self.H.add_hopping((((1, 1), (1, 1)), ((1, 0), (1, 0))),
                           z2pack.tb.vectors.neighbours([0, 1],
                                                        forward_only=True),
                           -t2,
                           phase=[1])

    # this test may produce false negatives due to small numerical differences
    def test_res1(self):
        self.createH(0.2, 0.3)
        # call to Z2Pack
        tb_system = z2pack.tb.System(self.H)
        tb_surface = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0])
        tb_surface.wcc_calc(verbose=False, num_strings=20, pickle_file=None)
        
        res = in_place_replace(tb_surface.get_res())

        self.assertFullAlmostEqual(tb_surface.get_res(), res)

    def test_res2(self):
        """ test pos_check=False """
        self.createH(0, 0.3)
        # call to Z2Pack
        tb_system = z2pack.tb.System(self.H)
        tb_surface = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0])
        tb_surface.wcc_calc(verbose=False,
                            num_strings=20,
                            pickle_file=None,
                            pos_tol=None)

        res = in_place_replace(tb_surface.get_res())

        self.assertFullAlmostEqual(tb_surface.get_res(), res)

    def test_res3(self):
        """ test gap_tol=None """
        self.createH(0.1, 0.3)
        # call to Z2Pack
        tb_system = z2pack.tb.System(self.H)
        tb_surface = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0])
        tb_surface.wcc_calc(verbose=False,
                            num_strings=20,
                            pickle_file=None,
                            gap_tol=None)

        res = in_place_replace(tb_surface.get_res())

        self.assertFullAlmostEqual(tb_surface.get_res(), res)

    def test_res4(self):
        """ test move_tol=None """
        self.createH(0.1, 0.3)
        # call to Z2Pack
        tb_system = z2pack.tb.System(self.H)
        tb_surface = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0])
        tb_surface.wcc_calc(verbose=False,
                          num_strings=20,
                          pickle_file=None,
                          move_tol=None)

        res = in_place_replace(tb_surface.get_res())

        self.assertFullAlmostEqual(tb_surface.get_res(), res)

    def test_res5(self):
        """ test gap_tol=None and move_tol=None"""
        self.createH(0.1, 0.3)
        # call to Z2Pack
        tb_system = z2pack.tb.System(self.H)
        tb_surface = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0])
        tb_surface.wcc_calc(verbose=False,
                            num_strings=20,
                            pickle_file=None,
                            gap_tol=None,
                            move_tol=None)

        res = in_place_replace(tb_surface.get_res())

        self.assertFullAlmostEqual(tb_surface.get_res(), res)

    def test_res6(self):
        """ Force convergence errors"""
        self.createH(0.1, 0.3)
        # call to Z2Pack
        tb_system = z2pack.tb.System(self.H)
        tb_surface = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0])
        tb_surface.wcc_calc(verbose=False,
                            num_strings=20,
                            pickle_file=None,
                            pos_tol=1e-12,
                            iterator=range(6, 10, 2),
                            gap_tol=1.,
                            move_tol=1e-12,
                            min_neighbour_dist=5e-3)

        res = in_place_replace(tb_surface.get_res())

        self.assertFullAlmostEqual(tb_surface.get_res(), res)

    def test_warning(self):
        """ test the warning that is given when string_vec != None"""
        self.createH(0.1, 0.3)
        # call to Z2Pack
        tb_system = z2pack.tb.System(self.H)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            tb_surface = tb_system.surface(lambda kx: [kx / 2, 0, 0], [0, 1, 0])
            assert len(w) == 1
            assert w[-1].category == DeprecationWarning
            assert "string_vec" in str(w[-1].message)

    def test_saveload(self):
        self.createH(0.1, 0.3)
        tb_system = z2pack.tb.System(self.H)
        surface1 = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=self._build_folder + '/tb_pickle.txt')
        surface2 = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=self._build_folder + '/tb_pickle.txt')
        surface1.wcc_calc(verbose=False)
        surface2.load()
        self.assertFullAlmostEqual(surface1.get_res(), surface2.get_res())

    def testkwargcheck1(self):
        """ test kwarg check on wcc_calc """
        self.createH(0.1, 0.3)
        # call to Z2Pack
        tb_system = z2pack.tb.System(self.H)
        tb_surface = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0])
        self.assertRaises(
            TypeError,
            tb_surface.wcc_calc,
            invalid_kwarg = 3)

    def testkwargcheck2(self):
        """ test kwarg check on __init__ """
        self.createH(0, 0.3)
        # call to Z2Pack
        tb_system = z2pack.tb.System(self.H)
        self.assertRaises(
            TypeError,
            tb_system.surface,
            1, 2, 0, invalid_kwarg = 3)

if __name__ == "__main__":
    unittest.main()
