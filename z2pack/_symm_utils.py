"""Utilitites to select the local symmetries of a surface from a list of all symmetries of the crystal"""

import numpy as np
import scipy.linalg as la
from fsc.export import export


@export
def round_to_zero(sym, tol=1e-10):
    """
    Round off values smaller than tol to zero.
    """
    for i in range(len(sym[0])):
        for j in range(len(sym[:, 0])):
            if (abs(sym[i, j]) < tol):
                sym[i, j] = 0.
    return sym


@export
def reduced_dist(k1, k2):
    """
    Calculates the distance between two vectors in reduced space.
    k1, k2: vector components given in reduced space
    """
    dist = []
    for x, y in zip(k1, k2):
        dist.append(min((x - y) % 1, (y - x) % 1))
    return dist


@export
def to_reciprocal(real_space):
    """
    Return basis in k space given basis in x space
    real_space: list of basis vectors [x1, x2, x3]
    """
    k_space = []
    c = np.dot(real_space[0], np.cross(real_space[1], real_space[2]))
    if abs(c) < 1e-5:
        raise ValueError("Unit cell not valid")
    for i in range(3):
        k_space.append(
            2 * np.pi / c *
            np.cross(real_space[(i + 1) % 3], real_space[(i + 2) % 3])
        )
    return k_space


@export
def reduced_symm(symm, basis):
    """
    Get symmetry matrix in reciprocal space in reduced basis from symmetry matrix in real space in cartesian basis
    symm: symmetry matrix in real space in cartesian coordinates
    basis: reduced basis of real space; basis vectors as columns
    """
    symm = symm.conj(
    )  # symmetry matrix in reciprocal space according to Sands, 1982
    bToE = basis  # basis trafo matrix from reduced to standard basis
    eToB = np.linalg.inv(bToE)
    symm = eToB.dot(symm).dot(bToE)
    return symm


@export
def find_local(symmetries, surface, precision=3, eps=1e-5):
    """
    Select those symmetries that leave all k-points on the surface invariant.
    symmetries: 3x3 symmetry matrix in reduced real space.
    surface : function t, s -> R^3, with the output being coordinates in the reduced basis
    precision: number of random k-points for which S(k) = k is checked
    """
    local_symmetries = []
    k_points = [surface(*list(np.random.rand(2))) for i in range(precision)]

    for symm in symmetries:
        k_symm = symm.conj()
        local = True
        for kp in k_points:
            if (la.norm(reduced_dist(kp, np.dot(k_symm, kp))) > eps):
                local = False
                break
        if (local):
            local_symmetries.append(symm)
    return local_symmetries
