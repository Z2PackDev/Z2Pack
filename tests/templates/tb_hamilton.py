#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 14:49:25 CEST
# File:    tb_hamilton.py

from common import *

import numpy as np

class TbHamiltonTestCase(CommonTestCase):

    def testH(self):
        H = z2pack.tb.Hamilton()

        # create the two atoms
        H.add_atom(([1, 1], 1), [0, 0, 0])
        H.add_atom(([-1, -1, 3], 1), [0.5, 0.6, 0.2])

        # add hopping between different atoms
        H.add_hopping(((0, 0), (1, 2)),
                      z2pack.tb.vectors.combine([0, -1], [0, -1], 0),
                      0.1,
                      phase=[1, -1j, 1j, -1])
        H.add_hopping(((0, 1), (1, 0)),
                      z2pack.tb.vectors.combine([0, -1], [0, -1], 0),
                      0.7,
                      phase=[1, 1j, -1j, -1])

        # add hopping between neighbouring orbitals of the same type
        H.add_hopping((((0, 0), (0, 0)), ((0, 1), (0, 1))),
                      z2pack.tb.vectors.neighbours([0, 1], forward_only=True),
                      -0.3,
                      phase=[1])
        H.add_hopping((((1, 1), (1, 1)), ((1, 0), (1, 0))),
                      z2pack.tb.vectors.neighbours([0, 1], forward_only=True),
                      -0.8,
                      phase=[1])
        H.add_hopping((((1, 1), (1, 1)), ((1, 0), (1, 0))),
                      [[1, 2, 3]],
                      -0.9,
                      phase=[1])
        M = in_place_replace(H._get_m([[0.4, 0, x] for x in np.linspace(0, 1, 13)]))

        self.assertFullAlmostEqual(H._get_m([[0.4, 0, x] for x in np.linspace(0, 1, 13)]), M)

if __name__ == "__main__":
    unittest.main()
