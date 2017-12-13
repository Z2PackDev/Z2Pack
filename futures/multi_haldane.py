#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import z2pack
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt

logging.getLogger('z2pack').setLevel(logging.WARNING)

# defining pauli matrices
identity = np.identity(2, dtype=complex)
pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)


def Hamilton_Haldane(k, m, t1, t2, phi):
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


def Hamilton(k, m, t1, t2, phi, signs):
    return la.block_diag(*[Hamilton_Haldane(k, m, t1, t2, s * phi) for s in signs])


def symmetry(n):
    return la.block_diag(*[np.diag([i, i]) for i in range(1, n + 1)])


def get_results(m, t1, t2, phi, signs):
    n = len(signs)
    system = z2pack.hm.System(lambda k: Hamilton(k, m, t1, t2, phi, signs), symm=symmetry(n))
    result = z2pack.surface.run(
        system=system,
        surface=lambda s, t: [t, s, 0.],
        min_neighbour_dist=1e-5,
        num_lines=101,
        move_tol=0.1,
        use_symm=True
    )
    return np.append([result], [result.symm_project(i) for i in range(1, n + 1)])


def title(i, c):
    s = "Unprojected Hamiltonian" if i == 0 else "Projection on $Eig_{{{}}}(S)$".format(i)
    s += "\n Chern number: {}".format(c)
    return s

if __name__ == "__main__":
    signs = [1, -1, -1]
    fig, ax = plt.subplots(1, len(signs) + 1, sharey='row', figsize=(10, 4))
    results = get_results(0.5, 1., 1. / 3., 0.5 * np.pi, signs)
    for i, r in enumerate(results):
        z2pack.plot.wcc(r, axis=ax[i], gaps=False)
        ax[i].set_title(title(i, int(round(z2pack.invariant.chern(r)))))
        ax[i].set_xlabel("$k_y$")
    ax[0].set_ylabel("WCC position")
    plt.tight_layout()
    plt.savefig("multi_haldane_model.pdf")
