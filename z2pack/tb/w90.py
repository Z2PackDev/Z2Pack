#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    10.02.2015 02:03:55 CET
# File:    hr_parse.py

from ..ptools.csv_parser import read_file
from .tight_binding import Hamilton as TbHamilton

import scipy.linalg as la

class Hamilton(TbHamilton):
    def __init__(self, hr_file, num_occ):
        super(Hamilton, self).__init__()
        
        num_wann, h_entries = _read_hr(hr_file)

        # initialize empty atom at the origin
        self.add_atom(([0] * num_wann, num_occ), [0, 0, 0])

        for hopping in h_entries:
            self.add_hopping(((0, hopping[1][0] - 1),(0, hopping[1][1] - 1)),
                             hopping[0],
                             hopping[2],
                             add_conjugate=False)
        
# read from seedname_hr.dat
def _read_hr(filename):
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

# read from seedname.wout
# TODO: check if the output is absolute or w.r.t. the reduced UC
def _read_centre(filename):
    with open(filename, 'r') as f:
        data = f.read().split('\n')

    for i, line in enumerate(data):
        if 'Final State' in line:
            start_line = i
            break
    else:
        raise ValueError('no WF centre final state found')

    positions = []
    for line in data[start_line + 1:]:
        if not 'WF centre and spread' in line:
            break
        line = line.split('(')[1].split(')')[0]
        line = [float(x) for x in line.split(',')]
        positions.append(line)
    return positions
