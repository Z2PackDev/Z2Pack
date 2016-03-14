#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    14.03.2016 10:29:04 CET
# File:    test_surface_run.py

import pytest

import numpy as np

import z2pack

@pytest.fixture(params=range(5, 21, 2))
def num_strings(request):
    return request.param

def test_simple(num_strings):
    system = z2pack.em.System(lambda k: np.eye(4))
    surface = lambda s, t: [0, 0, 0]
    result = z2pack.surface.run(system=system, surface=surface, num_strings=num_strings)
    assert result.wcc == [[0, 0]] * num_strings
    assert result.gap_size == [1] * num_strings
    assert result.gap_pos == [0.5] * num_strings
    assert result.ctrl_states == {}
