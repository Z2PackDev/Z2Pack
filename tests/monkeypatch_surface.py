#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.02.2016 10:10:52 MST
# File:    monkeypatch_surface.py

import pytest
import z2pack

@pytest.fixture
def patch_max_move(monkeypatch):
    monkeypatch.setattr(z2pack._core.surface._control, '_get_max_move', min)

class TrivialLineData:
    def __init__(self, val):
        self.wcc = val

class TrivialLineResult:
    def __init__(self, val):
        self.data = TrivialLineData(val)

class TrivialSurfaceLine:
    def __init__(self, val):
        self.result = TrivialLineResult(val)

class TrivialSurfaceData:
    def __init__(self, vals):
        self.lines = [TrivialSurfaceLine(val) for val in vals]
