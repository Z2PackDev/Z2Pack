#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 13:51:13 CEST
# File:    create_mmn_sample.py

import sys
sys.path.append('../../src')
import z2pack

import pickle

with open('mmn_read.txt', 'w') as f:
    f.write(str(z2pack.fp.read_mmn.getM('wannier90.mmn')))

if __name__ == "__main__":
    print("create_mmn_sample.py")
    
