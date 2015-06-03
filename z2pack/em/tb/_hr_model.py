#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    05.05.2015 12:04:36 CEST
# File:    _hr_hamilton.py

from ...ptools.csv_parser import read_file
from ._tb_model import Model

import numpy as np

class HrModel(Model):
    r"""A subclass of :class:`tb.Model` designed to read the
    tight-binding model from the ``*_hr.dat`` file produced by Wannier90.

    :param hr_file: Path to the ``*_hr.dat`` file.
    :type hr_file: str

    :param pos:   Positions of the orbitals. By default (positions = ``None``),
        all orbitals are put at the origin.
    :type pos:    list
    
    :param occ: Number of occupied states. Default: Half the number of orbitals.
    :type occ:  int

    :param h_cutoff: Minimum absolute value for hopping parameters to
        be included. This is useful if the ``hr_file`` contains many
        zero entries. Default: ``None`` (no hopping entries are excluded).
    :type h_cutoff: float
    """
    def __init__(self, hr_file, pos=None, occ=None, h_cutoff=None):
        
        num_wann, h_entries = _read_hr(hr_file)
        on_site = [0.] * num_wann
        if h_cutoff is not None:
            h_entries = [hopping for hopping in h_entries if (abs(hopping[3]) > h_cutoff)]
                             
        super(HrModel, self).__init__(on_site=on_site, hop=h_entries, pos=pos, occ=occ add_cc=False)
        
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
        h_entries.append([entry[3],
                          entry[4],
                          entry[:3],
                          (entry[5] + 1j * entry[6]) /
                          float(deg_pts[int(i / (num_wann * num_wann))])])

    return num_wann, h_entries
