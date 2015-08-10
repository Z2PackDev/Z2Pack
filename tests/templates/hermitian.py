#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    10.08.2015 13:28:03 CEST
# File:    hermitian.py


from common import *

import numpy as np

class HermitianTestCase(CommonTestCase):
    """
    Tests if the check for hermitian matrices works.
    """

    def non_hermitian(self, k, shift=0.):
        return np.array([[1, 1j + shift], [-1j, 0]])

    def test_throw(self):
        system = z2pack.em.System(lambda k: self.non_hermitian(k, shift=1e-5))
        surface = system.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04), pickle_file=None)
        self.assertRaises(ValueError, surface.wcc_calc, verbose=False)

    def test_nothrow(self):
        system = z2pack.em.System(lambda k: self.non_hermitian(k, shift=1e-5), hermitian_tol=1e-4)
        surface = system.surface(z2pack.shapes.Sphere([0., 0., 0.], 0.04), pickle_file=None)
        surface.wcc_calc(verbose=False)
        

if __name__ == "__main__":
    unittest.main()    
