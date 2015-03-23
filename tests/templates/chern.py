#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 10:22:43 CEST
# File:    tbexample.py

from common import *

import types
import unittest


class ChernTestCase(CommonTestCase):

    def createH(self, t1, t2):

        self.H = z2pack.tb.Hamilton()

        # create the two atoms
        self.H.add_atom(([1, 1], 1), [0, 0, 0])
        self.H.add_atom(([-1, -1], 1), [0.5, 0.5, 0])

        # add hopping between different atoms
        self.H.add_hopping(((0, 0), (1, 1)),
                           z2pack.tb.vectors.combine([0, -1], [0, -1], 0),
                           t1,
                           phase=[1, -1j, 1j, -1])
        self.H.add_hopping(((0, 1), (1, 0)),
                           z2pack.tb.vectors.combine([0, -1], [0, -1], 0),
                           t1,
                           phase=[1, 1j, -1j, -1])

        # add hopping between neighbouring orbitals of the same type
        self.H.add_hopping((((0, 0), (0, 0)), ((0, 1), (0, 1))),
                           z2pack.tb.vectors.neighbours([0, 1],
                                                        forward_only=True),
                           t2,
                           phase=[1])
        self.H.add_hopping((((1, 1), (1, 1)), ((1, 0), (1, 0))),
                           z2pack.tb.vectors.neighbours([0, 1],
                                                        forward_only=True),
                           -t2,
                           phase=[1])

    # this test may produce false negatives due to small numerical differences
    def test_chern(self):
        raise NotImplementedError('TODO')
        
if __name__ == "__main__":
    unittest.main()
