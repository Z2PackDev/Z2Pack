"""Tests for systems with explicit Hamiltonian matrix (hm)."""

# pylint: disable=redefined-outer-name

import numpy as np
import pytest
import z2pack

from hm_systems import weyl_surface  # pylint: disable=unused-import


def test_non_hermitian():
    """
    Test that setting a non-hermitian matrix raises.
    """
    hamilton = lambda k: np.array([[0, 1], [2, 0]])
    system = z2pack.hm.System(hamilton=hamilton)
    with pytest.raises(ValueError):
        z2pack.surface.run(system=system, surface=lambda s, t: [0, s, t])


@pytest.mark.parametrize("bands", [[1], None, 1])
def test_explicit_bands(bands, weyl_surface, compare_wcc):
    """
    Test setting the number of occupied bands explicitly.
    """
    system = z2pack.hm.System(
        lambda k: np.array([[k[2], k[0] - 1j * k[1]], [k[0] + 1j * k[1], -k[2]]]),
        bands=bands,
    )
    res = z2pack.surface.run(system=system, surface=weyl_surface)
    compare_wcc(res.wcc)


def test_non_periodic_raises():
    """
    Test that the check for periodicity of Hamiltonians raises when given a
    non-periodic value.
    """
    with pytest.raises(ValueError):
        system = z2pack.hm.System(  # pylint: disable=unused-variable
            lambda k: np.array([[k[2], k[0] - 1j * k[1]], [k[0] + 1j * k[1], -k[2]]]),
            check_periodic=True,
        )


def test_invalid_pos():
    """
    Test that trying to set too many positions raises.
    """
    with pytest.raises(ValueError):
        z2pack.hm.System(hamilton=lambda k: np.array([[0]]), pos=[[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]])
