#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    10.03.2015 10:24:40 CET
# File:    checkpoints.py

from common import *

import os
import re
import types
import shutil
import platform

class CheckpointTestCase(CommonTestCase):
    def __init__(self, *args, **kwargs):
        if(re.match('Windows', platform.platform(), re.IGNORECASE)):
            self._sep = '\\'
        else:
            self._sep = '/'
        self.build_folder = 'build' + self._sep + 'checkpoints'
        try:
            shutil.rmtree(self.build_folder)
        except OSError:
            pass
        os.mkdir(self.build_folder)
        self.pickle_file = self.build_folder + self._sep + 'chkpt.txt'

        super(CheckpointTestCase, self).__init__(*args, **kwargs)
        
    def createH(self, t1, t2):

        builder = z2pack.em.tb.Builder()

        # create the two atoms
        builder.add_atom([1, 1], [0, 0, 0], 1)
        builder.add_atom([-1, -1], [0.5, 0.5, 0], 1)

        # add hopping between different atoms
        builder.add_hopping(((0, 0), (1, 1)),
                           z2pack.em.tb.vectors.combine([0, -1], [0, -1], 0),
                           t1,
                           phase=[1, -1j, 1j, -1])
        builder.add_hopping(((0, 1), (1, 0)),
                           z2pack.em.tb.vectors.combine([0, -1], [0, -1], 0),
                           t1,
                           phase=[1, 1j, -1j, -1])

        # add hopping between neighbouring orbitals of the same type
        builder.add_hopping((((0, 0), (0, 0)), ((0, 1), (0, 1))),
                           z2pack.em.tb.vectors.neighbours([0, 1],
                                                        forward_only=True),
                           t2,
                           phase=[1])
        builder.add_hopping((((1, 1), (1, 1)), ((1, 0), (1, 0))),
                           z2pack.em.tb.vectors.neighbours([0, 1],
                                                        forward_only=True),
                           -t2,
                           phase=[1])
        self.model = builder.create()

    def test_strings_redone(self):
        self.createH(0.2, 0.3)
        system = z2pack.em.tb.System(self.model)
        surface = system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=self.pickle_file)
        surface.wcc_calc(verbose=False, num_strings=20, pos_tol=None, gap_tol=None, move_tol=None)
        res0 = surface.get_res()
        surface.wcc_calc(verbose=False, num_strings=20, pos_tol=1e-23, gap_tol=None, move_tol=None)
        res1 = surface.get_res()
        self.assertRaises(AssertionError, self.assertFullAlmostEqual, res0, res1)

    def test_num_strings(self):
        self.createH(0.2, 0.3)
        system = z2pack.em.tb.System(self.model)
        surface = system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=self.pickle_file)
        surface.wcc_calc(verbose=False, num_strings=20, pos_tol=None, gap_tol=None, move_tol=None)
        res0 = surface.get_res()
        surface.wcc_calc(verbose=False, num_strings=50, pos_tol=None, gap_tol=None, move_tol=None)
        res1 = surface.get_res()
        self.assertFullAlmostEqual(res0, res1)

    def test_load(self):
        self.createH(0.2, 0.3)
        system = z2pack.em.tb.System(self.model)

        surface0 = system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=self.pickle_file)
        surface0.wcc_calc(verbose=False, num_strings=20, pos_tol=None, gap_tol=None, move_tol=None)
        res0 = surface0.get_res()

        surface1 = system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=self.pickle_file)
        surface1.load()
        res1 = surface1.get_res()
        self.assertFullAlmostEqual(res0, res1)

    def test_conv_change(self):
        self.createH(0.2, 0.3)
        system = z2pack.em.tb.System(self.model)

        surface0 = system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=None)
        surface0.wcc_calc(verbose=False, num_strings=20, pos_tol=None)
        res0 = surface0.get_res()

        surface1 = system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=None)
        surface1.wcc_calc(verbose=False, num_strings=20, pos_tol=None, gap_tol=None, move_tol=None)
        surface1.wcc_calc(verbose=False, num_strings=20, pos_tol=None)
        res1 = surface1.get_res()
        self.assertFullAlmostEqual(res0, res1)

    def test_overwrite(self):
        self.createH(0.2, 0.3)
        system = z2pack.em.tb.System(self.model)
        surface = system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=self.pickle_file)
        surface.wcc_calc(verbose=False, num_strings=20, pos_tol=None, gap_tol=None, move_tol=None)
        surface.wcc_calc(verbose=False, num_strings=50, pos_tol=None, gap_tol=None, move_tol=None, overwrite=True)
        res = surface.get_res()
        assert(len(res['kpt']) == 50)
        
if __name__ == "__main__":
    unittest.main()
