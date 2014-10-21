#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 13:38:41 CEST
# File:    read_mmn.py

import sys
sys.path.append('../')
import z2pack

from common import *

import ast
import unittest


class ReadMmnTestCase(CommonTestCase):

    def test1(self):

        with open('./samples/mmn_read.txt', 'r') as f:
            tester = ast.literal_eval(f.read())

        self.assertContainerAlmostEqual(
            tester, z2pack.fp.read_mmn.getM('./samples/wannier90.mmn')
        )

if __name__ == "__main__":
    unittest.main()
