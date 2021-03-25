#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
A collection of functions for creating k-points input for different
first-principles codes.

All functions have the same calling structure as :func:`prototype`.
"""

import decorator
import numpy as np
from fsc.export import export


@export
def prototype(kpt):
    r"""
    Specifies the interface

    :param kpt:     The list of k-points in the string INCLUDING the
        final point which should not be in the calculation
    :type kpt:      :py:class:`list` of :py:obj:`numpy.array`
    """
    raise NotImplementedError('This is only the prototype for kpts')


@decorator.decorator
def _check_dim(fct, kpt):
    """Checks if all k-points are three-dimensional."""
    for k in kpt:
        if len(k) != 3:
            raise ValueError('Dimension of point k = {} != 3'.format(k))
    return fct(kpt)


@decorator.decorator
def _check_closed(fct, kpt):
    """Checks whether the k-point list forms a closed loop."""
    delta = kpt[-1] - kpt[0]
    if not np.isclose(np.round_(delta), delta).all():
        raise ValueError('The k-point line does not form a closed loop.')
    return fct(kpt)


@export
@_check_dim
@_check_closed
def abinit(kpt):
    """
    Creates a k-point input for **ABINIT**. It uses ``kptopt -1`` and specifies the k-points string using ``ndivk`` and ``kptbounds``.
    """
    _check_equal_spacing(kpt, 'ABINIT')
    start_point = kpt[0]
    last_point = kpt[-2]
    num_kpt = len(kpt) - 1

    string = "\nkptopt -1\nndivk " + str(int(num_kpt - 1)) + '\nkptbounds '
    for coord in start_point:
        string += str(coord).replace('e', 'd') + ' '
    string += '\n'
    for coord in last_point:
        string += str(coord).replace('e', 'd') + ' '
    string += '\n'
    return string


@export
@_check_dim
@_check_closed
def qe(kpt):  # pylint: disable=invalid-name
    """
    Creates a k-point input for  **Quantum Espresso**.
    """
    start_point = kpt[0]
    last_point = kpt[-2]
    num_kpt = len(kpt) - 1

    string = "\nK_POINTS crystal_b\n 2 \n"
    for coord in start_point:
        string += str(coord).replace('e', 'd') + ' '
    string += str(num_kpt - 1) + '\n'
    for coord in last_point:
        string += str(coord).replace('e', 'd') + ' '
    string += str(1) + '\n'
    return string


@export
@_check_dim
@_check_closed
def qe_explicit(kpt):
    """
    Creates a k-point input for **Quantum Espresso**, by explicitly specifying the k-points.
    """
    num_kpt = len(kpt) - 1

    string = "\nK_POINTS crystal\n {} \n".format(num_kpt)

    kpt_str = ((str(coord).replace('e', 'd') for coord in k) for k in kpt)

    for k in kpt_str:
        string += '{} {} {} 1\n'.format(*k)
    return string


@export
@_check_dim
@_check_closed
def wannier90(kpt):
    """
    Creates a k-point input for **Wannier90**. It can be useful when the first-principles code does not generate the k-points in ``wannier90.win`` (e.g. with Quantum Espresso).
    """
    num_kpt = len(kpt) - 1
    string = "mp_grid: " + str(int(num_kpt)) + " 1 1 \nbegin kpoints"
    for k in kpt[:-1]:
        string += '\n'
        for coord in k:
            string += str(coord).replace('e', 'd') + ' '
    string += '\nend kpoints\n'
    return string


@export
@_check_dim
@_check_closed
def wannier90_nnkpts(kpt):
    """
    Creates the nnkpts input to explicitly specify the nearest neighbours in wannier90.win
    """
    num_kpt = len(kpt) - 1
    bz_diff = [np.zeros(3, dtype=int) for _ in range(num_kpt - 1)]
    # check whether the last k-point is in a different UC
    bz_diff.append(np.array(np.round_(kpt[-1] - kpt[0]), dtype=int))
    string = 'begin nnkpts\n'
    for i, k in enumerate(bz_diff):
        j = (i + 1) % num_kpt
        string += ' {0:>3} {1:>3}    {2[0]: } {2[1]: } {2[2]: }\n'.format(
            i + 1, j + 1, k
        )
    string += 'end nnkpts\n'
    return string


@export
@_check_dim
@_check_closed
def wannier90_full(kpt):
    """
    Returns both k-point and nearest neighbour input for wannier90.win. This is the recommended function to use for Wannier90 2.1 and higher.
    """
    return wannier90(kpt) + '\n' + wannier90_nnkpts(kpt)


@export
@_check_dim
@_check_closed
def vasp(kpt):
    """
    Creates a k-point input for  **VASP**. It uses the automatic generation scheme with a Gamma centered grid. Note that VASP does **not** support any kind of k-point line **unless** they are exactly along one of the reciprocal lattice vectors, and the k-points are evenly spaced.
    """
    # VALIDITY CHECKS
    # check if the points are equally-spaced
    delta = _check_equal_spacing(kpt, 'VASP')

    num_kpt = len(kpt) - 1
    # check if it's positive x, y or z direction
    nonzero = []
    mesh = []
    for i, spacing in enumerate(delta):
        if np.isclose(spacing, 0):
            mesh.append('1')
        elif np.isclose(spacing, 1 / num_kpt):
            nonzero.append(i)
            mesh.append(str(num_kpt))
        else:
            raise ValueError(
                'The k-points must be aligned in (positive) kx-, ky- or kz-direction for VASP runs.'
            )
    mesh_str = ' '.join(mesh)

    if len(nonzero) != 1:
        raise ValueError(
            'The k-points can change only in kx-, ky- or kz direction for VASP runs. The given k-points change in {} directions.'
            .format(len(nonzero))
        )

    start_point = kpt[0]
    if not np.isclose(start_point[nonzero[0]], 0):
        raise ValueError(
            'The k-points must start at k{0} = 0 for VASP runs, since they change in k{0}-direction.'
            .format(['x', 'y', 'z'][nonzero[0]])
        )

    string = 'Automatic mesh\n0              ! number of k-points = 0 ->automatic generation scheme\nGamma          ! generate a Gamma centered grid\n'
    string += mesh_str + '        ! subdivisions\n'
    for coord in start_point:
        string += str(coord).replace('e', 'd') + ' '
    string += '         ! shift\n'
    return string


@export
@_check_dim
@_check_closed
def elk(kpt):
    """
    Creates a k-point input for  **ELK**. It uses the automatic generation scheme with a Gamma centered grid. Note that VASP does **not** support any kind of k-point line **unless** they are exactly along one of the reciprocal lattice vectors, and the k-points are evenly spaced.
    """
    # VALIDITY CHECKS
    # check if the points are equally-spaced
    delta = _check_equal_spacing(kpt, 'ELK')

    num_kpt = len(kpt) - 1
    # check if it's positive x, y or z direction
    nonzero = []
    mesh = []
    for i, spacing in enumerate(delta):
        if np.isclose(spacing, 0):
            mesh.append('1')
        elif np.isclose(spacing, 1 / num_kpt):
            nonzero.append(i)
            mesh.append(str(num_kpt))
        else:
            raise ValueError(
                'The k-points must be aligned in (positive) kx-, ky- or kz-direction for ELK runs.'
            )
    mesh_str = ' '.join(mesh)

    if len(nonzero) != 1:
        raise ValueError(
            'The k-points can change only in kx-, ky- or kz direction for ELK runs. The given k-points change in {} directions.'
            .format(len(nonzero))
        )
    

    start_point = kpt[0]
    if not np.isclose(start_point[nonzero[0]], 0):
        raise ValueError(
            'The k-points must start at k{0} = 0 for ELK runs, since they change in k{0}-direction.'
            .format(['x', 'y', 'z'][nonzero[0]])
        )
    s=wannier90_nnkpts(kpt)
    string=s+'\n\nngridk\n'+'1 1 '+str(num_kpt)+'\n\n'
    string+='vkloff\n'
    for coord in start_point:
        string+=str(coord).replace('e', 'd')+' '
    string+='\n'
    return string


def _check_equal_spacing(kpt, run_type):
    """Checks if the k-points are equally spaced, and throws an error if not. run_type is added in the error message."""
    deltas = [(k2 - k1) % 1 for k2, k1 in zip(kpt[1:], kpt[:-1])]
    for spacing in deltas[1:]:
        if not np.isclose(spacing, deltas[0]).all():
            raise ValueError(
                'The k-points must be equally spaced for {} runs.'.
                format(run_type)
            )

    return deltas[0]
