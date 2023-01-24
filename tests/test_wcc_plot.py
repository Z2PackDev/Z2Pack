"""Tests for the WCC plot function."""
# pylint: disable=redefined-outer-name,unused-argument,unused-wildcard-import,unexpected-keyword-arg

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import z2pack

from monkeypatch_data import *
from plottest_helpers import *


def test_wcc_plot(assert_image_equal, patch_surface_data):
    """Test WCC plot with passing an axis."""
    res = SurfaceData([[0, 1], [0.2, 0.9], [0.5, 0.6], [0.5, 0.5]], t_list=[0, 0.1, 0.5, 1.0])
    _, axis = plt.subplots()
    z2pack.plot.wcc(res, axis=axis)
    assert_image_equal("simple_wcc")


def test_no_axis_given(assert_image_equal, patch_surface_data):
    """Test WCC plot without passing an axis."""
    res = SurfaceData([[0, 1], [0.2, 0.9], [0.5, 0.6], [0.5, 0.5]], t_list=[0, 0.1, 0.5, 1.0])
    z2pack.plot.wcc(res)
    assert_image_equal("simple_wcc")  # this is intended to be the same as in wcc_plot


def test_no_gap(assert_image_equal, patch_surface_data):
    """Test WCC plot with passing an axis, without plotting the gaps."""
    res = SurfaceData([[0, 1], [0.2, 0.9], [0.5, 0.6], [0.5, 0.5]], t_list=[0, 0.1, 0.5, 1.0])
    _, axis = plt.subplots()
    z2pack.plot.wcc(res, axis=axis, gaps=False)
    assert_image_equal("wcc_no_gap")
