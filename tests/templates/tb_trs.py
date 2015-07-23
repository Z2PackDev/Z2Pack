#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 10:22:43 CEST
# File:    tb_example.py

from common import *

import os
import copy
import types
import shutil

class TbTrsExampleTestCase(BuildDirTestCase):

    def createH(self, t1, t2):

        builder = z2pack.em.tb.Builder()

        # create the two atoms
        builder.add_atom([1], [0, 0, 0], 1)
        builder.add_atom([-1], [0.5, 0.5, 0], 0)

        # add hopping between different atoms
        builder.add_hopping(((0, 0), (1, 0)),
                           z2pack.em.tb.vectors.combine([0, -1], [0, -1], 0),
                           t1,
                           phase=[1, -1j, 1j, -1])

        # add hopping between neighbouring orbitals of the same type
        builder.add_hopping(((0, 0), (0, 0)),
                           z2pack.em.tb.vectors.neighbours([0, 1],
                                                        forward_only=True),
                           t2,
                           phase=[1])
        builder.add_hopping(((1, 0), (1, 0)),
                           z2pack.em.tb.vectors.neighbours([0, 1],
                                                        forward_only=True),
                           -t2,
                           phase=[1])
        self.model = builder.create()
        self.trs_model = self.model.trs()

    # this test may produce false negatives due to small numerical differences
    def test_notrs(self):
        self.createH(0.2, 0.3)
        system = z2pack.em.tb.System(self.model)
        surface = system.surface(lambda kx, ky: [kx, ky, 0], pickle_file=None)
        surface.wcc_calc(verbose=False, num_strings=20)

        # explicitly compare to known results
        self.assertAlmostEqual(surface.chern()['chern'], 1.)

        # compare to old results
        res = in_place_replace(surface.get_res())

        self.assertFullAlmostEqual(res, surface.get_res())

    def test_trs(self):
        self.createH(0.2, 0.3)
        trs_system = z2pack.em.tb.System(self.trs_model)
        trs_surface = trs_system.surface(lambda kx, ky: [kx, ky, 0], pickle_file=None)
        trs_surface.wcc_calc(verbose=False, num_strings=20)

        trs_surface_z2 = trs_system.surface(lambda kx, ky: [kx / 2., ky, 0], pickle_file=None)
        trs_surface_z2.wcc_calc(verbose=False, num_strings=20)

        # explicitly compare to known results
        self.assertAlmostEqual(trs_surface.chern()['chern'], 0.)
        self.assertEqual(trs_surface_z2.z2(), 1)

        # compare to old results
        trs_res = in_place_replace(trs_surface.get_res())
        trs_res_z2 = in_place_replace(trs_surface_z2.get_res())

        self.assertFullAlmostEqual(trs_res, trs_surface.get_res())
        self.assertFullAlmostEqual(trs_res_z2, trs_surface_z2.get_res())

    def test_trs_inplace(self):
        self.createH(0.2, 0.3)\
        # create a second TRS model by in-place replacing
        model2 = copy.deepcopy(self.model)
        model2.trs(in_place=True)
        system0 = z2pack.em.tb.System(self.trs_model)
        surface0 = system0.surface(lambda kx, ky: [kx, ky, 0], pickle_file=None)
        surface0.wcc_calc(verbose=False, num_strings=20)
        system1 = z2pack.em.tb.System(model2)
        surface1 = system1.surface(lambda kx, ky: [kx, ky, 0], pickle_file=None)
        surface1.wcc_calc(verbose=False, num_strings=20)

        self.assertFullAlmostEqual(surface0.get_res(), surface1.get_res())

if __name__ == "__main__":
    unittest.main()
