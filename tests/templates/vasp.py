#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 14:49:25 CEST
# File:    fp_phony.py

from common import *

import os
import re
import types
import shutil
import unittest
import platform


class BiVaspTestCase(VaspTestCase):
    def __init__(self, *args, **kwargs):
        self._input_folder = 'samples/vasp'

        self._input_files = [self._input_folder + '/' + name for name in
                             ['CHGCAR', 'INCAR', 'POSCAR', 'POTCAR', 'wannier90.win']]

        super(BiVaspTestCase, self).__init__(*args, **kwargs)

        self.system = z2pack.fp.System(
            self._input_files,
            z2pack.fp.kpts.vasp,
            'KPOINTS',
            'mpirun $VASP >& log',
            build_folder=self._build_folder)

    def test_bismuth_0(self):
        surface = self.system.surface(lambda kx: [0, kx / 2, 0], [0, 0, 1], pickle_file=None)
        surface.wcc_calc(pos_tol=None, gap_tol=None, verbose=False, num_strings=4)
        res = in_place_replace(surface.get_res())
        self.assertFullAlmostEqual(res, surface.get_res())

    def test_bismuth_1(self):
        surface = self.system.surface(lambda kx: [0, kx, kx], [1, 0, 0], pickle_file=None)
        surface.wcc_calc(pos_tol=None, gap_tol=None, verbose=False, num_strings=4)
        res = in_place_replace(surface.get_res())
        self.assertFullAlmostEqual(res, surface.get_res())


if __name__ == "__main__":
    unittest.main()
