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
        M = [[[(0.99536826328310157-0.064747464977345695j), 0j], [0j, (0.99452189536827329-0.10452846326765346j)]], [[(0.96762793769258648-0.077241421373816455j), 0j], [0j, (0.99452189536827329-0.10452846326765346j)]], [[(0.9950000554748174-0.087507074372473237j), 0j], [0j, (0.99452189536827329-0.10452846326765348j)]], [[(0.96265477496457996-0.073352627805504514j), 0j], [0j, (0.99452189536827329-0.10452846326765344j)]], [[(0.99536826328310146-0.064747464977345695j), 0j], [0j, (0.99452189536827329-0.10452846326765344j)]], [[(0.96762793769258637-0.077241421373816496j), 0j], [0j, (0.99452189536827329-0.1045284632676535j)]], [[(0.99500005547481751-0.087507074372473057j), 0j], [0j, (0.9945218953682734-0.10452846326765337j)]], [[(0.96265477496457996-0.073352627805504667j), 0j], [0j, (0.99452189536827329-0.1045284632676535j)]], [[(0.99536826328310168-0.064747464977345681j), 0j], [0j, (0.99452189536827329-0.1045284632676535j)]], [[(0.96762793769258637-0.077241421373816344j), 0j], [0j, (0.9945218953682734-0.10452846326765337j)]], [[(0.9950000554748174-0.087507074372473265j), 0j], [0j, (0.99452189536827329-0.1045284632676535j)]], [[(0.96265477496457996-0.073352627805504569j), 0j], [0j, (0.99452189536827329-0.1045284632676535j)]]]

        self.assertFullAlmostEqual(system._m_handle([[0.4, 0, x] for x in np.linspace(0, 1, 13)]), M)

if __name__ == "__main__":
    unittest.main()
