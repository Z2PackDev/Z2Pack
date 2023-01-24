"""Test Chern plotting function."""
# pylint: disable=redefined-outer-name,unused-argument,unused-wildcard-import,unexpected-keyword-arg

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import z2pack

from monkeypatch_data import *
from plottest_helpers import *


def test_chern_plot(assert_image_equal, patch_surface_data):
    """Compare chern plot to reference image."""
    res = SurfaceData([[0, 1], [0.2, 0.9], [0.5, 0.6], [0.5, 0.5]], t_list=[0, 0.1, 0.5, 1.0])
    _, axis = plt.subplots()
    z2pack.plot.chern(res, axis=axis)
    assert_image_equal("simple_chern")


def test_chern_plot_no_axis(assert_image_equal, patch_surface_data):
    """
    Test chern plot function without passing in an axis.
    """
    res = SurfaceData([[0, 1], [0.2, 0.9], [0.5, 0.6], [0.5, 0.5]], t_list=[0, 0.1, 0.5, 1.0])
    z2pack.plot.chern(res)
    assert_image_equal("simple_chern")  # intentionally the same as before


def test_chern_plot_2(assert_image_equal, patch_surface_data):
    """Compare chern plot to reference image."""
    res = SurfaceData(
        [[0, 1], [0.2, 0.1], [0.3, 0.2], [0.4, 0.4], [0.5, 0.5]],
        t_list=[0, 0.1, 0.5, 0.9, 1.0],
    )
    _, axis = plt.subplots()
    z2pack.plot.chern(res, axis=axis)
    assert_image_equal("simple_chern_2")
