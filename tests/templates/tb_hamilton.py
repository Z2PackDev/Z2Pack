#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 14:49:25 CEST
# File:    tb_hamilton.py

from common import *

import numpy as np

class TbHamiltonTestCase(CommonTestCase):

    def testH(self):
        builder = z2pack.em.tb.Builder()

        # create the two atoms
        builder.add_atom([1, 1], [0, 0, 0], 1)
        builder.add_atom([-1, -1, 3], [0.5, 0.6, 0.2], 1)

        # add hopping between different atoms
        builder.add_hopping(((0, 0), (1, 2)),
                      z2pack.em.tb.vectors.combine([0, -1], [0, -1], 0),
                      0.1,
                      phase=[1, -1j, 1j, -1])
        builder.add_hopping(((0, 1), (1, 0)),
                      z2pack.em.tb.vectors.combine([0, -1], [0, -1], 0),
                      0.7,
                      phase=[1, 1j, -1j, -1])

        # add hopping between neighbouring orbitals of the same type
        builder.add_hopping((((0, 0), (0, 0)), ((0, 1), (0, 1))),
                      z2pack.em.tb.vectors.neighbours([0, 1], forward_only=True),
                      -0.3,
                      phase=[1])
        builder.add_hopping((((1, 1), (1, 1)), ((1, 0), (1, 0))),
                      z2pack.em.tb.vectors.neighbours([0, 1], forward_only=True),
                      -0.8,
                      phase=[1])
        builder.add_hopping((((1, 1), (1, 1)), ((1, 0), (1, 0))),
                      [[1, 2, 3]],
                      -0.9,
                      phase=[1])
        model = builder.create()
        system = z2pack.em.tb.System(model)
        M = in_place_replace(system._m_handle([[0.4, 0, x] for x in np.linspace(0, 1, 13)]))

        self.assertFullAlmostEqual(system._m_handle([[0.4, 0, x] for x in np.linspace(0, 1, 13)]), M)

if __name__ == "__main__":
    unittest.main()
