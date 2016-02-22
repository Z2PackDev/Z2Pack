#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    21.04.2015 09:13:01 CEST
# File:    weyl.py

import z2pack

import numpy as np
import matplotlib.pyplot as plt

# defining pauli matrices
pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
pauli_vector = list([pauli_x, pauli_y, pauli_z])

def hamilton0(k):
    """simple 2-band hamiltonian k.sigma with a Weyl point at k=0"""
    res = np.zeros((2, 2), dtype=complex)
    for kval, p_mat in zip(k, pauli_vector):
        res += kval * p_mat
    return res
def hamilton1(k):
    """2-band hamiltonian k.sigma with k_y -> -k_y"""
    k[2] = -k[2]
    res = np.zeros((2, 2), dtype=complex)
    for kval, p_mat in zip(k, pauli_vector):
        res += kval * p_mat
    return res

# creating the two systems
system0 = z2pack.em.System(hamilton0, occ=1)
system1 = z2pack.em.System(hamilton1) # occ=1 is default (#orbitals / 2)

# the surface is a sphere around the Weyl point
surface = z2pack.shapes.Sphere([0., 0., 0.], 0.01)
res0 = z2pack.surface.run(system=system0, surface=surface, move_tol=1e-2)
res1 = z2pack.surface.run(system=system1, surface=surface, gap_tol=0.4)

# plotting
fig, ax = plt.subplots(1, 2)

# plot styling
fs = 15
ax[0].set_xlabel(r'$\theta$', fontsize=fs)
ax[0].set_ylabel(r'$\bar{x}$', rotation='horizontal', fontsize=fs)
ax[1].set_xlabel(r'$\theta$', fontsize=fs)
ax[0].set_xticks([0, 1])
ax[1].set_xticks([0, 1])
ax[0].set_xticklabels([r'$0$', r'$\pi$'])
ax[1].set_xticklabels([r'$0$', r'$\pi$'])
ax[0].set_title(r'$\vec{k}.\vec{\sigma}$', fontsize=fs)
ax[1].set_title(r'$(k_x, -k_y, k_z).\vec{\sigma}$', fontsize=fs)

# plotting the evolution of polarization
#~ z2pack.surface.wcc_plot(res0, axis=ax[0])
#~ z2pack.surface.wcc_plot(res1, axis=ax[1])
z2pack.surface.chern_plot(res0, axis=ax[0])
z2pack.surface.chern_plot(res1, axis=ax[1])

plt.show()
