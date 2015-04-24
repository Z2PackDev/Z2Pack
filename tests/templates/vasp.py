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
        if(re.match('Windows', platform.platform(), re.IGNORECASE)):
            self._sep = '\\'
        else:
            self._sep = '/'
        self.input_folder = 'samples' + self._sep + 'vasp'
        self.build_folder = 'build' + self._sep + 'vasp' 

        self.input_files = [self.input_folder + self._sep + name for name in
                            ['CHGCAR', 'INCAR', 'POSCAR', 'POTCAR', 'wannier90.win']]

        super(BiVaspTestCase, self).__init__(*args, **kwargs)

    def test_bismuth(self):
        sys = z2pack.fp.System(
            self.input_files,
            z2pack.fp.kpts.vasp,
            'KPOINTS',
            'mpirun $VASP >& log',
            build_folder=self.build_folder)

        surface = sys.surface(lambda kx: [0, kx / 2, 0], [0, 0, 1], pickle_file=None)

        surface.wcc_calc(pos_tol=None, gap_tol=None, verbose=False)

        res = in_place_replace(surface.get_res())
        
        self.assertFullAlmostEqual(res, surface.get_res())


if __name__ == "__main__":
    unittest.main()
