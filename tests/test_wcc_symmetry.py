#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    14.03.2016 13:27:43 CET
# File:    test_wcc_plot.py

import pytest
import numpy as np
import matplotlib.pyplot as plt

import z2pack

from plottest_helpers import *

def test_weyl(assert_image_equal):
    system = z2pack.em.System(lambda k: np.array(
        [
            [k[2], k[0] -1j * k[1]],
            [k[0] + 1j * k[1], -k[2]]
        ]
    ))
    result = z2pack.surface.run(
        system=system,
        surface=z2pack.shapes.Sphere([0, 0, 0], 1.),
        num_strings=11,
        move_tol=None,
        gap_tol=None,
        pos_tol=None
    )
    fig, ax = plt.subplots()
    z2pack.surface.plot.wcc_symmetry(result, axis=ax, symmetry_operator=np.diag([1, -1]))
    assert_image_equal('simple_wcc_symmetry')

#~ def test_no_gap(assert_image_equal, patch_surface_data):
    #~ res = SurfaceData([[0, 1], [0.2, 0.9], [0.5, 0.6], [0.5, 0.5]], t_list=[0, 0.1, 0.5, 1.])
    #~ fig, ax = plt.subplots()
    #~ z2pack.surface.plot.wcc_symmetry(res, axis=ax, gaps=False)
    #~ assert_image_equal('wcc_symmetry_no_gap')
