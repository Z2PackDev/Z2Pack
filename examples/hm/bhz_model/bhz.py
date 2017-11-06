import logging

import z2pack
import numpy as np
import matplotlib.pyplot as plt

logging.getLogger('z2pack').setLevel(logging.WARNING)

pauli_y = np.array([[0, 1], [1, 0]], dtype=complex)
pauli_x = np.array([[0, -1j], [1j, 0]])
pauli_z = np.diag([1, -1])
pauli_vector = [pauli_x, pauli_y, pauli_z]


def bhz(A, B, C, D, M):
    def h(k):
        kx, ky = 2 * np.pi * np.array(k)
        d = [
            A * np.sin(kx), -A * np.sin(ky),
            -2 * B * (2 - (M / (2 * B)) - np.cos(kx) - np.cos(ky))
        ]
        H = sum(di * pi for di, pi in zip(d, pauli_vector))
        epsilon = C - 2 * D * (2 - np.cos(kx) - np.cos(ky))
        H += epsilon
        return H

    def Hamiltonian(k):
        return np.vstack([
            np.hstack([h(k), np.zeros((2, 2))]),
            np.hstack([np.zeros((2, 2)),
                       h(-np.array(k)).conjugate()])
        ])

    return Hamiltonian


def run(**kwargs):
    system = z2pack.hm.System(bhz(**kwargs), dim=2)
    res = z2pack.surface.run(system=system, surface=lambda s, t: [s / 2, t])
    z2pack.plot.wcc(res)
    plt.savefig('wcc_plot.pdf', bbox_inches='tight')
    print('Z2 invariant:', z2pack.invariant.z2(res))


if __name__ == '__main__':
    run(A=0.5, B=1., C=0., D=0., M=1.)
