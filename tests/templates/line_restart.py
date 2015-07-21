#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.07.2015 15:40:59 CEST
# File:    line_restart.py

from common import *


class LineRestartTestCase(BuildDirTestCase):

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

    # this test may produce false negatives due to small numerical differences
    def test_line(self):
        self.createH(0.3, 0.2)
        line = z2pack.em.tb.System(self.model).line(lambda x: [0.5 * x, 0.24, 0.])
        line.wcc_calc(verbose=False)
        line.wcc_calc(verbose=False)
        line.wcc_calc(pos_tol=0.0008, verbose=False)

if __name__ == "__main__":
    unittest.main()
