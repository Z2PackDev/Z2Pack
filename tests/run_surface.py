#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    07.09.2015 16:34:46 CEST
# File:    run_line.py

from common import *
import numpy as np

# defining pauli matrices
pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)
pauli_vector = list([pauli_x, pauli_y, pauli_z])

def hamilton(k):
    """simple 2-band hamiltonian k.sigma with a Weyl point at k=0"""
    res = np.zeros((2, 2), dtype=complex)
    for kval, p_mat in zip(k, pauli_vector):
        res += kval * p_mat
    return res

system = z2pack.em.System(hamilton)
z2pack.run_surface(system, lambda s, t: [s, t, 0])
