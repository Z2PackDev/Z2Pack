#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    22.09.2014 14:23:12 CEST
# File:    squarelattice.py

import itertools

import pytest
import z2pack
import tbmodels

@pytest.fixture
def tb_system():
    t1, t2 = (0.2, 0.3)

    model = tbmodels.Model(
        on_site=(1, 1, -1, -1), 
        pos=[
            [0., 0., 0.], 
            [0., 0., 0.], 
            [0.5, 0.5, 0.], 
            [0.5, 0.5, 0.]
        ],
        occ=2
    )

    for p, R in zip([1, 1j, -1j, -1], itertools.product([0, -1], [0, -1], [0])):
        model.add_hop(overlap=p * t1, orbital_1=0, orbital_2=2, R=R)
        model.add_hop(overlap=p.conjugate() * t1, orbital_1=1, orbital_2=3, R=R)

    for R in ((r[0], r[1], 0) for r in itertools.permutations([0, 1])):
        model.add_hop(t2, 0, 0, R)
        model.add_hop(t2, 1, 1, R)
        model.add_hop(-t2, 2, 2, R)
        model.add_hop(-t2, 3, 3, R)

    return z2pack.tb.System(model)

@pytest.fixture
def tb_surface():
    return lambda s, t: [s, t, 0]
