#!/usr/bin/python3
import os
import pickle
import subprocess

import z2pack
z2pack.serializer.set(pickle)
import scipy.linalg as la
import numpy as np

# directories
qedir = '/home/greschd/software/espresso-5.2.1/bin'
wandir = '/home/greschd/software/wannier90-2.0.1'
mpirun = 'mpirun -np 4'

# commands
pwcmd = ' '.join([mpirun, qedir + '/pw.x '])
pw2wancmd = ' '.join([mpirun, qedir + '/pw2wannier90.x'])
# --> here i use the build_nnkp.py script to build the nnkp file instead of using wannier90.x
# note that this script use the wannier90 input file *win
z2cmd = ' '.join([
    'python ../build_nnkp.py MoP2_ICSD_37222.win;',
    pwcmd, "< MoP2_ICSD_37222.nscf.in >& pw.log;",
    pw2wancmd, "< MoP2_ICSD_37222.pw2wan.in >& pw2wan.log;"
])

# Settings used for wcc_calc.
settings = {'num_strings': 11,
            'pos_tol': 1e-2,
            'gap_tol': 2e-2,
            'move_tol': 0.3,
            'iterator': range(8, 13, 2),
            'min_neighbour_dist': 1e-3,
            'save_file': 'res.p',
            }

# run the scf calculation
if not os.path.isdir('scf/MoP2.save'):
    print("Running the scf calculation")
    subprocess.call(pwcmd+" < MoP2_ICSD_37222.scf.in > scf.out", cwd='scf', shell=True)

# creating the z2pack.qe object
print("Running z2pack calculation")
MoP2_ICSD_37222 = z2pack.fp.System(
    input_files = [os.path.join('input', name) for name in os.listdir('input')],
    kpt_fct=[z2pack.fp.kpoint.qe, z2pack.fp.kpoint.wannier90],
    kpt_path=["MoP2_ICSD_37222.nscf.in", "MoP2_ICSD_37222.win"],
    command=z2cmd,
    build_folder='build',
    executable='/bin/bash',
    mmn_path='MoP2_ICSD_37222.mmn'
)
#
# function to go around a sphere in k-space in cartesian coordinate
#
# first i define the matrix to go from cart. coord. to cryst. coord.
alat = 10.9734612033510022    # lattice parameter in bohrradius
bohr = 0.529177249            # bohr to angstrom
b = 2 * np.pi / (alat * bohr) * np.array([
    [1.000000, 1.637277, 0.000000],
    [0.000000,  1.918509,  0.000000],
    [0.000000,  0.000000,  1.165671]
])  # reciprocal lattice
binv = la.inv(b)  # matrix to go from cartesian to crystal coordinate

# center of the sphere in cryst. coord.
center = [6.27041621e-01,  2.72351861e-01,  0.0000000000]
# radius of the sphere in Ang^-1
radius = 0.02


def f(t, k):
    center_cart = np.dot(b.T, center)
    if(t == 0):
        t = 0.01
    if(t == 1):
        t = 0.99
    x, y, z = center_cart
    x += radius * np.cos(2 * np.pi * k) * np.sin(np.pi * t)
    y += radius * np.sin(2 * np.pi * k) * np.sin(np.pi * t)
    z -= radius * np.cos(np.pi * t)
    xx = [x, y, z]
    res = np.dot(binv.T, xx)
    xx = res[0] * b[0] + res[1] * b[1] + res[2] * b[2]
    return res

#
# Running z2pack
#
result = z2pack.surface.run(
    system=MoP2_ICSD_37222,
    surface=f,
    **settings
)
