#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    05.05.2015 13:59:00 CEST
# File:    hr_hamilton.py

from common import *

import numpy as np

class HrHamiltonTestCase(CommonTestCase):
    
    def testH(self):
        model = z2pack.em.tb.HrModel('./samples/hr_hamilton.dat', occ=28)
        system = z2pack.em.tb.System(model)
        M = in_place_replace(system._m_handle([[0.4, 0, x] for x in np.linspace(0, 1, 3)]))
        self.assertFullAlmostEqual(system._m_handle([[0.4, 0, x] for x in np.linspace(0, 1, 3)]), M)
        
    def test_error(self):
        self.assertRaises(ValueError, z2pack.em.tb.HrModel, './samples/hr_hamilton.dat', occ=28, pos=[[1., 1., 1.]])

if __name__ == "__main__":
    unittest.main()
