#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    10.02.2015 02:03:55 CET
# File:    hr_parse.py

from ..ptools.csv_parser import read_file

def _read(filename):
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
    for entry in data[2]:
        h_entries.append([entry[:3], (entry[3], entry[4]), entry[5] + 1j * entry[6]])

    return num_wann, nrpts, deg_pts, h_entries
