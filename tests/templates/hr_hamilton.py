#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    05.05.2015 13:59:00 CEST
# File:    hr_hamilton.py

from common import *

import numpy as np

class HrHamiltonTestCase(CommonTestCase):
    
    def testH(self):
        H = z2pack.tb.HrHamilton('./samples/hr_hamilton.dat', 28)
        M = in_place_replace(H._get_m([[0.4, 0, x] for x in np.linspace(0, 1, 3)]))
        self.assertFullAlmostEqual(H._get_m([[0.4, 0, x] for x in np.linspace(0, 1, 3)]), M)
        
    def test_error(self):
        self.assertRaises(ValueError, z2pack.tb.HrHamilton, './samples/hr_hamilton.dat', 28, [[1., 1., 1.]])

if __name__ == "__main__":
    unittest.main()
