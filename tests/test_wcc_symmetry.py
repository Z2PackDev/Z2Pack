#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pytest
import numpy as np

import z2pack

from plottest_helpers import *


def test_weyl(assert_image_equal):
    system = z2pack.hm.System(lambda k: np.array(
        [
            [k[2], k[0] -1j * k[1]],
            [k[0] + 1j * k[1], -k[2]]
        ]
    ))
    result = z2pack.surface.run(
        system=system,
        surface=z2pack.shape.Sphere([0, 0, 0], 1.),
        num_lines=11,
        move_tol=None,
        gap_tol=None,
        pos_tol=None
    )
    fig, ax = plt.subplots()
    z2pack.plot.wcc_symmetry(
        result, axis=ax, symmetry_operator=np.diag([1, -1])
    )
    assert_image_equal('simple_wcc_symmetry')


def test_weyl_no_axis(assert_image_equal):
    system = z2pack.hm.System(lambda k: np.array(
        [
            [k[2], k[0] -1j * k[1]],
            [k[0] + 1j * k[1], -k[2]]
        ]
    ))
    result = z2pack.surface.run(
        system=system,
        surface=z2pack.shape.Sphere([0, 0, 0], 1.),
        num_lines=11,
        move_tol=None,
        gap_tol=None,
        pos_tol=None
    )
    z2pack.plot.wcc_symmetry(result, symmetry_operator=np.diag([1, -1]))
    assert_image_equal(
        'simple_wcc_symmetry'
    )  # intentionally the same as before
