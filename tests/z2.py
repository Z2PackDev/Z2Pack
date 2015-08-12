#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    13.04.2015 16:52:29 CEST
# File:    z2.py

from common import *

import numpy as np

class Z2TestCase(CommonTestCase):

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

    def test_z2_1(self):
        self.createH(0.2, 0.3)
        # call to Z2Pack
        tb_system = z2pack.em.tb.System(self.model)
        tb_surface = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=None)
        tb_surface.wcc_calc(verbose=False, num_strings=20)
        
        res = 1

        self.assertFullAlmostEqual(tb_surface.z2(), res)

    def test_z2_2(self):
        """ test pos_check=False """
        self.createH(0, 0.3)
        # call to Z2Pack
        tb_system = z2pack.em.tb.System(self.model)
        tb_surface = tb_system.surface(lambda kx, ky: [kx / 2, ky, 0], pickle_file=None)
        tb_surface.wcc_calc(verbose=False,
                            num_strings=20,
                            pos_tol=None)

        res = 0

        self.assertFullAlmostEqual(tb_surface.z2(), res)


if __name__ == "__main__":
    unittest.main()    
