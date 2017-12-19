"""Tests for calculating invariants in symmetry eigenspaces for hm systems"""

import numpy as np
import scipy.linalg as la
import pytest
import z2pack


def hamilton_haldane(k, s):
    # set fixed parameters
    m, t1, t2, phi = 0.5, 1., 1. / 3., s * 0.5 * np.pi
    # defining pauli matrices
    identity = np.identity(2, dtype=complex)
    pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
    pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)

    k_a = 2 * np.pi / 3. * np.array([
        -k[0] - k[1], 2. * k[0] - k[1], -k[0] + 2. * k[1]
    ])
    k_b = 2 * np.pi * np.array([k[0], -k[0] + k[1], k[1]])
    H = 2 * t2 * np.cos(phi) * sum([np.cos(-val) for val in k_b]) * identity
    H += t1 * sum([np.cos(-val) for val in k_a]) * pauli_x
    H += t1 * sum([np.sin(-val) for val in k_a]) * pauli_y
    H += m * pauli_z
    H -= 2 * t2 * np.sin(phi) * sum([np.sin(-val) for val in k_b]) * pauli_z
    return H


def hamilton(k, signs):
    return la.block_diag(*[hamilton_haldane(k, s) for s in signs])


def symmetry(n):
    return la.block_diag(*[np.diag([i, i]) for i in range(1, n + 1)])


def get_results(signs):
    n = len(signs)
    system = z2pack.hm.System(lambda k: hamilton(k, signs), symm=symmetry(n))
    result = z2pack.surface.run(
        system=system,
        surface=lambda s, t: [t, s, 0.],
        min_neighbour_dist=1e-5,
        num_lines=101,
        move_tol=0.1,
        use_symm=True
    )
    chern_total = z2pack.invariant.chern(result)
    res_projected = [result.symm_project(i) for i in range(1, n + 1)]
    chern_projected = [z2pack.invariant.chern(r) for r in res_projected]
    return chern_total, chern_projected


@pytest.mark.parametrize(
    'signs', [[1], [1, 1], [1, -1], [1, -1, -1], [1, 1, 1, 1]]
)
def test_multi_haldane(signs):
    chern_total, chern_projected = get_results(signs)
    print(chern_total, chern_projected)
    # check that chern numbers are whole numbers
    assert np.isclose(chern_total, round(chern_total))
    assert np.allclose(chern_projected, np.round(chern_projected))
    assert np.isclose(np.sum(signs), -1 * chern_total)
    assert np.allclose(signs, -1 * np.array(chern_projected))
