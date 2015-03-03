# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 14:49:25 CEST
# File:    tb_hamilton.py

import sys
sys.path.insert(0, '../')
import z2pack

from common import *

import re
import platform
import types
import unittest


class FpPhonyTestCase(CommonTestCase):
    def __init__(self, *args, **kwargs):
        if(re.match('Windows', platform.platform(), re.IGNORECASE)):
            self._sep = '\\'
        else:
            self._sep = '/'

        super(FpPhonyTestCase, self).__init__(*args, **kwargs)

    def testphony1(self):
        sys = z2pack.fp.System(
            'samples' + self._sep + 'wannier90.mmn',
            lambda x, y, z, N: '',
            "kpts",
            "",
            build_folder='samples' + self._sep + 'build')

        surface = sys.surface(lambda kx: [0, kx / 2, 0], [0, 0, 1], use_pickle=False)

        surface.wcc_calc(pos_check=False, gap_check=False, verbose=False)
        self.assertDictAlmostEqual(
            surface.get_res(), in_place_replace(surface.get_res()))

    def testphony2(self):
        sys = z2pack.fp.System(
            'samples' + self._sep + 'varw90.mmn',
            lambda x, y, z, N: '',
            "kpts",
            "",
            build_folder='samples' + self._sep + 'build',
            file_names='wannier90.mmn')

        surface = sys.surface(lambda kx: [0, kx / 2, 0], [0, 0, 1], use_pickle=False)

        surface.wcc_calc(pos_check=False, gap_check=False, verbose=False)
        self.assertDictAlmostEqual(
            surface.get_res(), in_place_replace(surface.get_res()))


    def testphony3(self):
        sys = z2pack.fp.System(
            'samples' + self._sep + 'varw90.mmn',
            lambda x, y, z, N: '',
            "kpts",
            "",
            build_folder='samples' + self._sep + 'build',
            mmn_path='varw90.mmn')

        surface = sys.surface(lambda kx: [0, kx / 2, 0], [0, 0, 1], use_pickle=False)

        surface.wcc_calc(verbose=False)
        self.assertDictAlmostEqual(
            surface.get_res(), in_place_replace(surface.get_res()))


if __name__ == "__main__":
    unittest.main()
