#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import z2pack

import numpy as np
from sortedcontainers import SortedList

from z2pack.line import WccLineData as LineData
from z2pack.surface import SurfaceData

from z2pack.line import LineResult

@pytest.fixture
def patch_max_move(monkeypatch):
    monkeypatch.setattr(z2pack.surface._control, '_get_max_move', min)

@pytest.fixture
def patch_surface_data(monkeypatch):
    def __init__(self, wcc_list, t_list=None):
        if t_list is None:
            t_list = np.linspace(0, 1, len(wcc_list))
        self.lines = SortedList(key=lambda x: x.t)
        for t, wcc in zip(t_list, wcc_list):
            self.add_line(t, LineResult(LineData(wcc), tuple(), tuple()))
    monkeypatch.setattr(SurfaceData, '__init__', __init__)
