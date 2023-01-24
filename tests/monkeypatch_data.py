"""
Fixtures that monkeypatch Data classes so that they can simply be set to the desired value.
"""

import numpy as np
import pytest
from sortedcontainers import SortedList

import z2pack
from z2pack.line import LineResult
from z2pack.line import WccLineData as LineData
from z2pack.surface import SurfaceData


@pytest.fixture
def patch_max_move(monkeypatch):
    """
    Take the minimum of all WCC instead of actually computing the maximum movement.
    """
    monkeypatch.setattr(
        z2pack.surface._control, "_get_max_move", min  # pylint: disable=protected-access
    )


@pytest.fixture
def patch_surface_data(monkeypatch):
    """
    Monkeypatch the SurfaceData class so that it can be set from a nested list of WCC and list of t-values.
    """

    def __init__(self, wcc_list, t_list=None):
        if t_list is None:
            t_list = np.linspace(0, 1, len(wcc_list))
        self.lines = SortedList(key=lambda x: x.t)
        for t, wcc in zip(t_list, wcc_list):
            self.add_line(t, LineResult(LineData(wcc), tuple(), tuple()))

    monkeypatch.setattr(SurfaceData, "__init__", __init__)
