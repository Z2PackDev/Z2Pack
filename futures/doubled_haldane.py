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


def Hamilton_part(k, m, t1, t2, phi):
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
    # signs = [sign for m, sign for phi]
    return la.block_diag(
        Hamilton_part(k, m, t1, t2, phi), Hamilton_part(k, signs[0] * m, t1, t2, signs[1] * phi)
    )


def get_results(m, t1, t2, phi, signs):
    system = z2pack.hm.System(lambda k: Hamilton(k, m, t1, t2, phi, signs), symm=np.diag([1, 1, -1, -1]), bands=2)
    result = z2pack.surface.run(
        system=system,
        surface=lambda s, t: [t, s, 0.],
        min_neighbour_dist=1e-5,
        num_lines=101,
        use_symm=True
    )
    return [result, result.symm_project(1), result.symm_project(-1)]

def sign_name(s):
    d = ['-', '0', '+']
    return [d[1+s[0]], d[1+s[1]]]

if __name__ == "__main__":
    fig, ax = plt.subplots(4, 3, sharey='row', figsize=(12, 18))
    for i, s in enumerate(zip([1, 1, -1, -1], [1, -1, 1, -1])):
        results = get_results(0.5, 1., 1. / 3., 0.5 * np.pi, signs=s)
        z2pack.plot.wcc(results[0], axis=ax[i][0])
        z2pack.plot.wcc(results[1], axis=ax[i][1])
        z2pack.plot.wcc(results[2], axis=ax[i][2])
        ax[i][0].set_title("WCCs of Double Haldane model ({}m, {}$\phi$)".format(*sign_name(s)))
        ax[i][1].set_title("WCCs in +1 eigenspace ({}m, {}$\phi$)".format(*sign_name(s)))
        ax[i][2].set_title("WCCs in -1 eigenspace ({}m, {}$\phi$)".format(*sign_name(s)))
        chern_number = [z2pack.invariant.chern(results[j]) for j in [0, 1, 2]]
        print("Doubled Haldane model with {}m and {}phi:".format(*sign_name(s)))
        print("Chern number:", chern_number[0])
        print("Symmetry eigenspace of eigenvalue 1:")
        print("Chern number:", chern_number[1])
        print("Symmetry eigenspace of eigenvalue -1:")
        print("Chern number:", chern_number[2])



    plt.tight_layout()
    plt.savefig("double_haldane_model.pdf")
