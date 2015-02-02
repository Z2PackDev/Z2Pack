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
            'samples' + self._sep + 'build',
            "")

        plane = sys.plane(lambda kx: [0, kx, 0], [0, 0, 1], use_pickle=False)

        plane.wcc_calc(no_iter=True, no_neighbour_check=True, verbose=False)
        self.assertDictAlmostEqual(
            plane.get_res(), in_place_replace(plane.get_res()))

    def testphony2(self):
        sys = z2pack.fp.System(
            'samples' + self._sep + 'varw90.mmn',
            lambda x, y, z, N: '',
            "kpts",
            'samples' + self._sep + 'build',
            "",
            file_names='wannier90.mmn')

        plane = sys.plane(lambda kx: [0, kx, 0], [0, 0, 1], use_pickle=False)

        plane.wcc_calc(no_iter=True, no_neighbour_check=True, verbose=False)
        self.assertDictAlmostEqual(
            plane.get_res(), in_place_replace(plane.get_res()))


    def testphony3(self):
        sys = z2pack.fp.System(
            'samples' + self._sep + 'varw90.mmn',
            lambda x, y, z, N: '',
            "kpts",
            'samples' + self._sep + 'build',
            "",
            mmn_path='varw90.mmn')

        plane = sys.plane(lambda kx: [0, kx, 0], [0, 0, 1], use_pickle=False)

        plane.wcc_calc(verbose=False)
        self.assertDictAlmostEqual(
            plane.get_res(), in_place_replace(plane.get_res()))


if __name__ == "__main__":
    unittest.main()
