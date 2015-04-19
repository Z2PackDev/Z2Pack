#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    10.03.2015 10:53:12 CET
# File:    quietload.py


from common import *

import types

class QuietLoadTestCase(CommonTestCase):
    def test_q(self):
        system = z2pack.System(lambda kx, N: [])
        surface = system.surface(lambda kx: [0, 0, kx], [1, 0, 0], pickle_file='samples/dummy.txt')
        surface.load(quiet=True)
        
    def test_nq(self):
        system = z2pack.System(lambda kx, N: [])
        surface = system.surface(lambda kx: [0, 0, kx], [1, 0, 0], pickle_file='samples/dummy.txt')
        self.assertRaises(IOError, surface.load)
        
if __name__ == "__main__":
    unittest.main()
    
