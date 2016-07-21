#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.07.2016 17:10:29 CEST
# File:    test_read_mmn.py

import json

import pytest
import z2pack
import numpy as np

def test_read(compare_data):
    compare_data(lambda x, y: np.equal(x, y).all(), z2pack.fp._read_mmn.get_m('samples/mmn/bi.mmn'))

def test_false_path():
    with pytest.raises(IOError):
        z2pack.fp._read_mmn.get_m('invalid_path')
