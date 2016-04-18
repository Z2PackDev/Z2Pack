#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Gabriel Autès, Dominik Gresch <greschd@gmx.ch>
# Date:    18.04.2016 13:46:06 CEST
# File:    build_nnkp.py

import re
import sys
import functools
import contextlib

import numpy as np

# read input
with open(sys.argv[1], 'r') as fin:
    nk = 0
    kpts = []
    a = []
    bohr = 0.52917721
    re_assign = re.compile('[=:]')
    normalize = lambda l: re.sub(re_assign, ' ', l, count=1).split()
    for line in fin:
        if 'exclude_bands' in line:
            data = re.compile('[,;]').split(' '.join(normalize(line)[1:]))
            exclude = []
            for part in data:
                try:
                    exclude_min, exclude_max = (int(x) for x in part.split("-"))
                    exclude.extend(range(exclude_min, exclude_max + 1))
                except ValueError:
                    exclude.append(int(part))
        if 'mp_grid' in line:
            data = line.replace("=", " ").replace(":,", " ").split()[1:4]
            nk1, nk2, nk3 = (int(x) for x in data)
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
with open(seedname + '.nnkp', 'w') as fout, contextlib.redirect_stdout(fout):
    print('File created by build_nnkp.py from ', sys.argv[1])
    print()
    print('calc_only_A  :  F')
    print()
    print('begin real_lattice')
    for i in range(3):
        print('%16.8f %16.8f %16.8f' % tuple([bohr * x for x in a[i]]))
    print('end real_lattice')
    print()
    print('begin recip_lattice')
    print('%16.8f %16.8f %16.8f' % tuple(b1))
    print('%16.8f %16.8f %16.8f' % tuple(b2))
    print('%16.8f %16.8f %16.8f' % tuple(b3))
    print('end recip_lattice')
    print()
    print('begin kpoints')
    print('%4i' % (nk))
    for k in kpts:
        print('{:16.8} {:16.8} {:16.8}'.format(*k))
    print('end kpoints')
    print()
    print('begin spinor_projections')
    print('     0')
    print('end spinor_projections')
    print()
    print('begin nnkpts')
    print('    2')
    for i in range(nk):
        print('%5i %5i    0    0    0' % (
            i + 1, i + 2 if i + 2 != nk + 1 else 1))
        print('%5i %5i    0    0    0' % (i + 1, i if i != 0 else nk))
    print('end nnkpts')
    print()
    print('begin exclude_bands')
    print(len(exclude))
    for exc in sorted(exclude):
        print(exc)
    print('end exclude_bands')
