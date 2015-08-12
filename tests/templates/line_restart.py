#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.07.2015 15:40:59 CEST
# File:    line_restart.py

from common import *

import pickle

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
    def test_restart_1(self):
        self.createH(0.3, 0.2)
        line = z2pack.em.tb.System(self.model).line(lambda x: [0.5 * x, 0.24, 0.])
        line2 = z2pack.em.tb.System(self.model).line(lambda x: [0.5 * x, 0.24, 0.])
        line.wcc_calc(verbose=False)
        line.wcc_calc(pos_tol=0.0008, verbose=False)
        line2.wcc_calc(pos_tol=0.0008, verbose=False)
        self.assertFullAlmostEqual(line.get_res(), line2.get_res())

    def test_restart_2(self):
        """
        Check different restart scenarios.
        """
        self.createH(0.3, 0.2)
        line = z2pack.em.tb.System(self.model).line(lambda x: [0.5 * x, 0.24, 0.])
        line.wcc_calc(verbose=False, pos_tol=1e-12, iterator=range(5, 20, 2))
        # make sure evaluation fails
        del line._m_handle
        # exact match when pos_tol=None
        line.wcc_calc(verbose=False, pos_tol=None, iterator=19)
        # higher pos_tol -> already reached
        line.wcc_calc(verbose=False, pos_tol=5e-3)
        # lower pos_tol -> error
        self.assertRaises(AttributeError, line.wcc_calc, verbose=False, pos_tol=1e-3)
        # false N -> error
        self.assertRaises(AttributeError, line.wcc_calc, verbose=False, pos_tol=None, iterator=[18])

    def test_restart_3(self):
        self.createH(0.3, 0.2)
        line = z2pack.em.tb.System(self.model).line(lambda x: [0.5 * x, 0.24, 0.])
        line.wcc_calc(verbose=False, pos_tol=1e-12, iterator=range(5, 10, 2))
        # make sure evaluation fails
        del line._m_handle
        # no fast-forwarding due to previous max < N
        self.assertRaises(AttributeError, line.wcc_calc, verbose=False, pos_tol=1e-12, iterator=29)
        # fast-forward past the iterator end
        line.wcc_calc(verbose=False, pos_tol=1e-12, iterator=range(3, 8, 2))

    def test_pickle(self):
        self.createH(0.3, 0.2)
        line = z2pack.em.tb.System(self.model).line(lambda x: [0.5 * x, 0.24, 0.])
        line.wcc_calc(verbose=False)
        with open(self._build_folder + 'res_pickle.txt', 'wb') as f:
            pickle.dump(line, f)
        with open(self._build_folder + 'res_pickle.txt', 'rb') as f:
            line2 = pickle.load(f)
        self.assertFullAlmostEqual(line.get_res(), line2.get_res())
        

if __name__ == "__main__":
    unittest.main()
