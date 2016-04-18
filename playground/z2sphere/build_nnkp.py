#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Gabriel Autès, Dominik Gresch <greschd@gmx.ch>
# Date:    18.04.2016 13:46:06 CEST
# File:    build_nnkp.py

import sys
import operator
import functools

import numpy as np

# read input
with open(sys.argv[1], 'r') as fin:
    nk = 0
    kpts = []
    a = []
    bohr = 0.52917721
    for line in fin:
        if 'exclude_bands' in line:
            # TODO: generalize to include not only min-max statements
            data = line.replace("=", " ").replace(":,", " ").split()[1]
            exclude_min = int(data.split("-")[0])
            exclude_max = int(data.split("-")[1])
            nexclude = exclude_max - exclude_min + 1
        if 'mp_grid' in line:
            data = line.replace("=", " ").replace(":,", " ").split()[1:]
            nk1, nk2, nk3 = (int(x) for x in data[1:4])
            nk = nk1 * nk2 * nk3

        if 'begin' in line and 'kpoints' in line:
            nextline = next(fin)
            while('end' not in nextline):
                kpts.append([float(x.replace('d', 'e').replace('D', 'E'))
                             for x in nextline.split()])
                nextline = next(fin)
        if 'begin' in line and 'unit_cell_cart' in line:
            nextline = next(fin)
            nextline = next(fin)
            while('end' not in nextline):
                a.append([float(x) for x in nextline.split()])
                nextline = next(fin)

# recip lattice
b1 = np.cross(a[1], a[2])
n1 = np.dot(b1, a[0]) * bohr
b1 = 2 * np.pi / n1 * b1
b2 = np.cross(a[2], a[0])
n2 = np.dot(b2, a[1]) * bohr
b2 = 2 * np.pi / n2 * b2
b3 = np.cross(a[0], a[1])
n3 = np.dot(b3, a[2]) * bohr
b3 = 2 * np.pi / n3 * b3

# output
seedname = sys.argv[1].split(".")[0]
fout = open(seedname + '.nnkp', 'w')

print >> fout, 'File created by build_nnkp.py from ', sys.argv[1]
print >> fout, ''
print >> fout, 'calc_only_A  :  F'
print >> fout, ''
print >> fout, 'begin real_lattice'
for i in range(3):
    print >> fout, '%16.8f %16.8f %16.8f' % tuple([bohr * x for x in a[i]])
print >> fout, 'end real_lattice'
print >> fout, ''
print >> fout, 'begin recip_lattice'
print >> fout, '%16.8f %16.8f %16.8f' % tuple(b1)
print >> fout, '%16.8f %16.8f %16.8f' % tuple(b2)
print >> fout, '%16.8f %16.8f %16.8f' % tuple(b3)
print >> fout, 'end recip_lattice'
print >> fout, ''
print >> fout, 'begin kpoints'
print >> fout, '%4i' % (nk)
for i in range(nk):
    print >> fout, '%16.8f %16.8f %16.8f' % tuple(kpts[i])
print >> fout, 'end kpoints'
print >> fout, ''
print >> fout, 'begin spinor_projections'
print >> fout, '     0'
print >> fout, 'end spinor_projections'
print >> fout, ''
print >> fout, 'begin nnkpts'
print >> fout, '    2'
for i in range(nk):
    print >> fout, '%5i %5i    0    0    0' % (
        i + 1, i + 2 if i + 2 != nk + 1 else 1)
    print >> fout, '%5i %5i    0    0    0' % (i + 1, i if i != 0 else nk)
print >> fout, 'end nnkpts'
print >> fout, ''
print >> fout, 'begin exclude_bands'
print >> fout, '%4i' % (nexclude)
for i in range(exclude_min, exclude_max + 1):
    print >> fout, '%4i' % (i)
print >> fout, 'end exclude_bands'
