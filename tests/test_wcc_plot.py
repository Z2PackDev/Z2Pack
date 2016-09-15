#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    14.03.2016 13:27:43 CET
# File:    test_wcc_plot.py

import pytest
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import z2pack

from plottest_helpers import *
from monkeypatch_data import *

def test_wcc_plot(assert_image_equal, patch_surface_data):
    res = SurfaceData([[0, 1], [0.2, 0.9], [0.5, 0.6], [0.5, 0.5]], t_list=[0, 0.1, 0.5, 1.])
    fig, ax = plt.subplots()
    z2pack.plot.wcc(res, axis=ax)
    assert_image_equal('simple_wcc')

def test_no_axis_given(assert_image_equal, patch_surface_data):
    res = SurfaceData([[0, 1], [0.2, 0.9], [0.5, 0.6], [0.5, 0.5]], t_list=[0, 0.1, 0.5, 1.])
    z2pack.plot.wcc(res)
    assert_image_equal('simple_wcc') # this is intended to be the same as in wcc_plot

def test_no_gap(assert_image_equal, patch_surface_data):
    res = SurfaceData([[0, 1], [0.2, 0.9], [0.5, 0.6], [0.5, 0.5]], t_list=[0, 0.1, 0.5, 1.])
    fig, ax = plt.subplots()
    z2pack.plot.wcc(res, axis=ax, gaps=False)
    assert_image_equal('wcc_no_gap')
