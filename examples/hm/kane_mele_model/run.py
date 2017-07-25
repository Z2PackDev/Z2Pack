#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import z2pack
import numpy as np
from numpy import cos, sin, kron, sqrt
import matplotlib.pyplot as plt

logging.getLogger('z2pack').setLevel(logging.WARNING)

# defining pauli matrices
identity = np.identity(2, dtype=complex)
pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)

def get_kane_mele_hamiltonian(t, lambda_v, lambda_R, lambda_SO):
    def inner(k):
        k = np.array(k) * 2 * np.pi
        kx, ky = k
        # change to reduced coordinates
        x = (kx - ky) / 2
        y = (kx + ky) / 2
        return (
            t * (1 + 2 * cos(x) * cos(y)) * kron(pauli_x, identity) +
            lambda_v * kron(pauli_z, identity) +
            lambda_R * (1 - cos(x) * cos(y)) * kron(pauli_y, pauli_x) +
            -sqrt(3) * lambda_R * sin(x) * sin(y) * kron(pauli_y, pauli_y) +
            2 * t * cos(x) * sin(y) * kron(pauli_y, identity) +
            lambda_SO * (2 * sin(2 * x) - 4 * sin(x) * cos(y)) * kron(pauli_z, pauli_z) +
            lambda_R * cos(x) * sin(y) * kron(pauli_x, pauli_x) +
            -sqrt(3) * lambda_R * sin(x) * cos(y) * kron(pauli_x, pauli_y)
        )
    return inner

if __name__ == '__main__':
    system = z2pack.hm.System(
        get_kane_mele_hamiltonian(
            t=1, lambda_v=0.1, lambda_R=0.05, lambda_SO=0.06
        ),
        dim=2,
        check_periodic=True
    )
    res = z2pack.surface.run(system=system, surface=lambda s, t: [s / 2, t])
    print('Z2 invariant: {}'.format(z2pack.invariant.z2(res)))
    fig, ax = plt.subplots(figsize=[5, 3])
    z2pack.plot.wcc(res, axis=ax)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['0', '0.5'])
    ax.set_xlabel(r'$k_y$')
    ax.set_yticks([0, 1])
    ax.set_ylabel(r'$\bar{y}$', rotation='horizontal')
    plt.savefig('plot.pdf', bbox_inches='tight')
