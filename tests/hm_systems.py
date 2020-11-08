"""
Fixtures for hamiltonian matrix (hm) system tests.
"""
# pylint: disable=redefined-outer-name,invalid-name

import numbers

import pytest
import numpy as np

import z2pack


class OverlapMockSystem(z2pack.system.OverlapSystem):
    """
    OverlapSystem which just wraps an EigenstateSystem and creates the overlap matrix.
    """
    def __init__(self, eigenstate_system):
        self.eigenstate_system = eigenstate_system

    def get_mmn(self, kpt, use_symm=False):
        return [
            z2pack.line.EigenstateLineData(
                *self.eigenstate_system.get_eig(kpt)
            ).overlaps, None
        ]


@pytest.fixture(
    params=[-1., -0.8, -0.6, -0.4, -0.2, 0., 0.2, 0.4, 0.6, 0.8, 1.]
)
def kz(request):
    return request.param


@pytest.fixture(params=[10**n for n in range(-4, -1)])
def pos_tol(request):
    return request.param


@pytest.fixture(params=[False, True])
def simple_system(request):
    """
    Return a system where the Hamiltonian is the identity, either as eigenstates or overlap system.
    """
    res = z2pack.hm.System(lambda k: np.eye(4))
    if request.param:
        res = OverlapMockSystem(res)
    return res


def _check_real(func):
    """
    Decorator that checks that the args passed to the function are reals.
    """
    def inner(*args):
        for x in args:
            assert isinstance(x, numbers.Real)
        return func(*args)

    return inner


@pytest.fixture
def simple_line():
    return _check_real(lambda t: [0, 0, 0])


@pytest.fixture
def simple_surface():
    return _check_real(lambda s, t: [0, 0, 0])


@pytest.fixture
def simple_volume():
    return _check_real(lambda t1, t2, t3: [0, 0, 0])


@pytest.fixture(params=[False, True])
def weyl_system(request):
    """
    Creates a Weyl point system.
    """
    res = z2pack.hm.System(
        lambda k: np.array([[k[2], k[0] - 1j * k[1]],
                            [k[0] + 1j * k[1], -k[2]]])
    )
    if request.param:
        res = OverlapMockSystem(res)
    return res


def weyl_line_creator(kz):
    return lambda t: [np.cos(t * 2 * np.pi), np.sin(t * 2 * np.pi), kz]


weyl_line = pytest.fixture(weyl_line_creator)


@pytest.fixture
def weyl_surface():
    return z2pack.shape.Sphere([0, 0, 0], 1.)
