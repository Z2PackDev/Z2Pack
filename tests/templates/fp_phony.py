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


class FpPhonyTestCase(BuildDirTestCase):
    def testphony1(self):
        sys = z2pack.fp.System(
            'samples/wannier90.mmn',
            lambda x: '',
            "kpts",
            "",
            build_folder=self._build_folder)

        surface = sys.surface(lambda kx: [0, kx / 2, 0], [0, 0, 1], pickle_file=None)

        surface.wcc_calc(pos_tol=None, gap_tol=None, verbose=False)
        self.assertFullAlmostEqual(
            surface.get_res(), in_place_replace(surface.get_res()))

    def testphony2(self):
        sys = z2pack.fp.System(
            'samples/varw90.mmn',
            lambda x: '',
            "kpts",
            "",
            build_folder=self._build_folder,
            file_names='wannier90.mmn')

        surface = sys.surface(lambda kx: [0, kx / 2, 0], [0, 0, 1], pickle_file=None)

        surface.wcc_calc(pos_tol=None, gap_tol=None, verbose=False)
        self.assertFullAlmostEqual(
            surface.get_res(), in_place_replace(surface.get_res()))


    def testphony3(self):
        sys = z2pack.fp.System(
            'samples/varw90.mmn',
            lambda x: '',
            "kpts",
            "",
            build_folder=self._build_folder,
            mmn_path='varw90.mmn')

        surface = sys.surface(lambda kx: [0, kx / 2, 0], [0, 0, 1], pickle_file=None)

        self.assertRaises(ValueError, surface.wcc_calc, verbose=False)
        self.assertFullAlmostEqual(
            surface.get_res(), in_place_replace(surface.get_res()))

    def test_warnings(self):
        """
        test the warning that is given if new style surfaces are used
        """
        sys = z2pack.fp.System(
            'samples/varw90.mmn',
            lambda x: '',
            "kpts",
            "",
            build_folder=self._build_folder,
            mmn_path='varw90.mmn')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            surface = sys.surface(lambda kx, ky: [ky, kx / 2, 0], pickle_file=None)
            assert len(w) == 1
            assert w[-1].category == UserWarning
            assert "recommended to use string_vec != None" in str(w[-1].message)

if __name__ == "__main__":
    unittest.main()
