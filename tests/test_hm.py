#!/usr/bin/env python
# -*- coding: utf-8 -*-

import z2pack
import pytest
import numpy as np

from hm_systems import weyl_surface

def test_non_hermitian():
    H = lambda k: np.array([[0, 1], [2, 0]])
    system = z2pack.hm.System(hamilton=H, check_periodic=True)
    with pytest.raises(ValueError):
        z2pack.surface.run(
            system=system,
            surface=lambda s, t: [0, s, t]
        )

@pytest.mark.parametrize('bands', [[1], None, 1])
def test_explicit_bands(bands, weyl_surface, compare_wcc):
    system = z2pack.hm.System(
        lambda k: np.array(
            [
                [k[2], k[0] -1j * k[1]],
                [k[0] + 1j * k[1], -k[2]]
            ]
        ),
        bands=bands
    )
    res = z2pack.surface.run(system=system, surface=weyl_surface)
    compare_wcc(res.wcc)

def test_invalid_pos():
    with pytest.raises(ValueError):
        system = z2pack.hm.System(
            hamilton=lambda k: np.array([[0]]),
            pos=[[0., 0., 0.], [0.5, 0.5, 0.5]]
        )
