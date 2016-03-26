#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Authors:  Dominik Gresch <greschd@gmx.ch>, Gabriel Autes
# Date:    27.09.2014 21:27:27 CEST
# File:    kpts.py
r"""
A collection of functions for creating k-points input for different
first-principles codes.

All functions have the same calling structure as :func:`prototype`.
"""

import numpy as np

def prototype(kpt):
    r"""
    Specifies the interface

    :param kpt:     The list of k-points in the string INCLUDING the
        final point which should not be in the calculation
    :type kpt:      list of numpy arrays
    """
    raise NotImplementedError('This is only the prototype for kpts')


def abinit(kpt):
    """
    Creates a k-point input for **ABINIT**. It uses ``kptopt -1`` and specifies the k-points string using ``ndivk`` and ``kptbounds``.
    """
    start_point = kpt[0]
    end_point = kpt[-1]
    last_point = kpt[-2]
    N = len(kpt) - 1
    for point in kpt:
        if len(point) != 3:
            raise ValueError('dimension of point != 3')

    string = "\nkptopt -1\nndivk " + str(int(N - 1)) + '\nkptbounds '
    for coord in start_point:
        string += str(coord).replace('e', 'd') + ' '
    string += '\n'
    for coord in last_point:
        string += str(coord).replace('e', 'd') + ' '
    string += '\n'
    return string


def qe(kpt):
    """
    Creates a k-point input for  **Quantum Espresso**.
    """
    start_point = kpt[0]
    end_point = kpt[-1]
    last_point = kpt[-2]
    N = len(kpt) - 1
    for point in kpt:
        if len(point) != 3:
            raise ValueError('dimension of point != 3')

    string = "\nK_POINTS crystal_b\n 2 \n"
    for coord in start_point:
        string += str(coord).replace('e', 'd') + ' '
    string += str(N-1)+'\n'
    for coord in last_point:
        string += str(coord).replace('e', 'd') + ' '
    string += str(1)+'\n'
    return string

def wannier90(kpt):
    """
    Creates a k-point input for **Wannier90**. It can be useful when the first-principles code does not generate the k-points in ``wannier90.win`` (e.g. with Quantum Espresso).
    """
    for point in kpt:
        if len(point) != 3:
            raise ValueError('dimension of point != 3')

    N = len(kpt) - 1
    string = "mp_grid: " + str(int(N)) + " 1 1 \nbegin kpoints"
    for k in kpt[:-1]:
        string += '\n'
        for coord in k:
            string += str(coord).replace('e', 'd') + ' '
    string += '\nend kpoints\n'
    return string

# FOR A FUTURE VERSION WHEN VASP MIGHT SUPPORT EXPLICIT K-POINTS
#~
#~ def vasp(kpt):
    #~ """
    #~ Creates a k-point input for  **VASP**, using explicit points
    #~ """
            #~
    #~ for point in kpt:
        #~ if len(point) != 3:
            #~ raise ValueError('dimension of point != 3')
            #~
    #~ N = len(kpt) - 1
    #~ string = 'Explicit k-points\n' + str(N) + '\nReciprocal\n'
    #~ for k in kpt[:-1]:
        #~ string += '{0} {1} {2} 1.'.format(*list(k))
        #~ string += '\n'
    #~ return string

def vasp(kpt):
    """
    Creates a k-point input for  **VASP**. It uses the automatic generation scheme with a Gamma centered grid. Note that VASP does **not** support any kind of k-point line **unless** they are exactly along one of the reciprocal lattice vectors, and the k-points are evenly spaced.

    TODO: check -- what does VASP do about the order of the k-points?
    """
    
    for point in kpt:
        if len(point) != 3:
            raise ValueError('dimension of point != 3')

    # VALIDITY CHECKS
    # check if the points are equally-spaced
    deltas = [(k2 - k1) % 1 for k2, k1 in zip(kpt[1:], kpt[:-1])]
    for d in deltas[1:]:
        if not all(np.isclose(d, deltas[0]).flatten()):
            raise ValueError('The k-points must be equally spaced for VASP runs.')

    delta = deltas[0]
    N = len(kpt) - 1
    # check if it's positive x, y or z direction
    nonzero = []
    mesh = []
    for i, d in enumerate(delta):
        if np.isclose(d, 0):
            mesh.append('1')
        elif np.isclose(d, 1 / N):
            nonzero.append(i)
            mesh.append(str(N))
        else:
            raise ValueError('The k-points must be aligned in (positive) kx-, ky- or kz-direction for VASP runs.')
    mesh = ' '.join(mesh)

    if len(nonzero) != 1:
        raise ValueError('The k-points can change only in kx-, ky- or kz direction for VASP runs. The given k-points change in {} directions.'.format(len(nonzero)))

    start_point = kpt[0]
    if not np.isclose(start_point[nonzero[0]], 0):
        raise ValueError('The k-points must start at k{0} = 0 for VASP runs, since they change in k{0}-direction.'.format(['x', 'y', 'z'][nonzero[0]]))

    string = 'Automatic mesh\n0              ! number of k-points = 0 ->automatic generation scheme\nGamma          ! generate a Gamma centered grid\n'
    string += mesh + '        ! subdivisions\n'
    for coord in start_point:
        string += str(coord).replace('e', 'd') + ' '
    string += '         ! shift\n'
    return string
