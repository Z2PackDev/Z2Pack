#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:  Dominik Gresch <greschd@ethz.ch>, Gabriel Autes
# Date:    27.09.2014 21:27:27 CEST
# File:    kpts.py
r"""
A collection of functions for creating k-points input for different 
first-principles codes.

All functions have the same calling structure as :func:`prototype`.
"""


def prototype(kpt):
    r"""
    Specifies the interface

    :param kpt:     The list of k-points in the string INCLUDING the
        final point which should not be in the calculation
    :type kpt:      list
    """
    raise NotImplementedError('This is only the prototype for kpts')

#~ 
#~ def abinit(kpt):
    #~ """
    #~ Creates a k-point input for **ABINIT**. It uses ``kptopt -1`` and
    #~ specifies the k-points string using ``ndivk`` and ``kptbounds``.
    #~ """
    #~ for point in [start_point, last_point, end_point]:
        #~ if len(point) != 3:
            #~ raise ValueError('dimension of point != 3')
#~ 
    #~ string = "\nkptopt -1\nndivk " + str(int(N - 1)) + '\nkptbounds '
    #~ for coord in start_point:
        #~ string += str(coord).replace('e', 'd') + ' '
    #~ string += '\n'
    #~ for coord in last_point:
        #~ string += str(coord).replace('e', 'd') + ' '
    #~ string += '\n'
    #~ return string
#~ 
#~ 
#~ def qe(kpt):
    #~ """
    #~ Creates a k-point input for  **Quantum Espresso**.
    #~ """
    #~ for point in [start_point, last_point, end_point]:
        #~ if len(point) != 3:
            #~ raise ValueError('dimension of point != 3')
#~ 
    #~ string = "\nK_POINTS crystal_b\n 2 \n"
    #~ for coord in start_point:
        #~ string += str(coord).replace('e', 'd') + ' '
    #~ string += str(N-1)+'\n'
    #~ for coord in last_point:
        #~ string += str(coord).replace('e', 'd') + ' '
    #~ string += str(1)+'\n'
    #~ return string
#~ 
#~ def wannier90(kpt):
    #~ """
    #~ Creates a k-point input for **Wannier90**. It can be useful when the
    #~ first-principles code does not generate the k-points in
    #~ ``wannier90.win`` (e.g. with Quantum Espresso).
    #~ """
    #~ for point in [start_point, last_point, end_point]:
        #~ if len(point) != 3:
            #~ raise ValueError('dimension of point != 3')
#~ 
    #~ string = "mp_grid: " + str(int(N)) + " 1 1 \nbegin kpoints"
    #~ for i in range(N):
        #~ string += '\n'
        #~ point = start_point
        #~ for j, coord in enumerate(point):
            #~ coord += float(i)/float(N-1) * (last_point[j] - start_point[j])
            #~ string += str(coord).replace('e', 'd') + ' '
    #~ string += '\nend kpoints\n'
    #~ return string

def vasp(kpt):
    """
    Creates a k-point input for  **VASP**. It uses explicit k-points
    """
    # N or N - 1?
    N = len(kpt) - 1
    string = 'Explicit k-points\n' + str(N) + '\nReciprocal\n'
    for k in kpt[:-1]:
        string += '{} {} {} 1.'.format(*list(k))
    string += '\n'
    return string
