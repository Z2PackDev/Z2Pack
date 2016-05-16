#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    21.04.2015 09:13:01 CEST
# File:    weyl.py

import numpy as np
import matplotlib.pyplot as plt

import z2pack

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

# creating the two systems
system0 = z2pack.em.System(hamilton0, bands=1)

# the surface is a sphere around the Weyl point
surface = z2pack.shapes.Sphere([0., 0., 0.], 0.01)
res = z2pack.surface.run(
    system=system0, 
    surface=surface, 
    save_file='results/res.msgpack',
    load=True
)
res2 = z2pack.surface.run(
    system=system0, 
    surface=surface, 
    num_strings=21,
    save_file='results/res.msgpack',
    load=True,
    )

# plotting
fig, ax = plt.subplots()

# plot styling
fs = 15
ax.set_xlabel(r'$\theta$', fontsize=fs)
ax.set_ylabel(r'$\bar{x}$', rotation='horizontal', fontsize=fs)
ax.set_xticks([0, 1])
ax.set_xticklabels([r'$0$', r'$\pi$'])
ax.set_title(r'$\vec{k}.\vec{\sigma}$', fontsize=fs)

# plotting the evolution of polarization
z2pack.surface.plot.chern(res, axis=ax)

plt.savefig('plot.pdf', bbox_inches='tight')
