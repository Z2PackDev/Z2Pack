#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    05.05.2015 12:04:36 CEST
# File:    _hr_hamilton.py

from ..ptools.csv_parser import read_file
from ._tight_binding import Hamilton

import numpy as np

class HrHamilton(Hamilton):
    r"""A subclass of :class:`tb.Hamilton` designed to read the
    tight-binding models from the ``*_hr.dat`` file produced by Wannier90.

    :param hr_file: Path to the ``*_hr.dat`` file.
    :type hr_file: str

    :param num_occ: Number of occupied bands.
    :type num_occ: int

    :param positions: Positions of the orbitals described in the ``*_hr.dat``
        file, w.r.t the reduced unit cell.
        Per default, all orbitals are put at the origin.
    :type positions: list

    :param h_cutoff: Minimum absolute value for hopping parameters to
        be included. This is useful if the ``hr_file`` contains many
        zero entries. Default: ``None`` (no hopping entries are excluded).
    :type h_cutoff: float
    """
    def __init__(self, hr_file, num_occ, positions=None, h_cutoff=None):
        super(HrHamilton, self).__init__()
        
        num_wann, h_entries = _read_hr(hr_file)
        if h_cutoff is not None:
            h_entries = [hopping for hopping in h_entries if (abs(hopping[2]) > h_cutoff)]
        if positions is None:
            positions = [[0., 0., 0.]] * num_wann
        if not num_wann == len(positions):
            raise ValueError(
                'the number of positions given ({0})'.format(len(positions)) +
                ' does not match the number of bands ({})'.format(num_wann)
                )

        # initialize atoms - first atom creates all electrons
        self.add_atom(([0], num_occ), positions[0])
        for pos in positions[1:]:
            self.add_atom(([0], 0), list(pos))
        # add hopping terms
        for hopping in h_entries:
            self.add_hopping(((hopping[1][0] - 1, 0),(hopping[1][1] - 1, 0)),
                             hopping[0],
                             hopping[2],
                             add_conjugate=False)
        
def _read_hr(filename):
    r"""
    read the number of wannier functions and the hopping entries
    from *hr.dat
    """
    data = read_file(filename, separator=" ", ignore=[0])

    num_wann = data[0][0][0]
    nrpts = data[0][1][0]

    deg_pts = []
    for line in data[1]:
        deg_pts.extend(line)
    if len(data) == 4:
        deg_pts.extend(data[2][0])
        del data[2]

    assert(len(deg_pts) == nrpts)

    h_entries = []
    for i, entry in enumerate(data[2]):
        h_entries.append([entry[:3],
                          (entry[3], entry[4]),
                          (entry[5] + 1j * entry[6]) /
                          float(deg_pts[int(i / (num_wann * num_wann))])])

    return num_wann, h_entries
