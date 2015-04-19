#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 13:38:41 CEST
# File:    read_mmn.py


from common import *

import ast

class ReadMmnTestCase(CommonTestCase):

    def test1(self):
        
        with open('./samples/mmn_read.txt', 'r') as f:
            if sys.version_info[:2] == (2, 6):
                tester = eval(f.read())
            else:
                tester = ast.literal_eval(f.read())

        self.assertFullAlmostEqual(
            tester, z2pack.fp._read_mmn.getM('./samples/wannier90.mmn')
        )

if __name__ == "__main__":
    unittest.main()
