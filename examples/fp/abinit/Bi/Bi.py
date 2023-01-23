#!/usr/bin/env python

import os
import shutil
import subprocess

import z2pack

"""
Bismuth example
"""

ABINIT_PATH = "/home/greschd/software/abinit-9.8.1/src/98_main/abinit"

if not os.path.exists("./scf_files"):
    shutil.copytree("./scf_input", "./scf_files")
    subprocess.check_call(
        f"{ABINIT_PATH} < Bi_scf.files >& log",
        shell=True,
        cwd="./scf_files",
        executable="/bin/bash",
    )

if not os.path.exists("./results"):
    os.makedirs("./results")

# creating the System object
# the command (mpirun ...) will have to be replaced
Bi = z2pack.fp.System(
    input_files=["input/Bi_nscf.files", "input/Bi_nscf.in", "input/wannier90.win"],
    kpt_fct=z2pack.fp.kpoint.abinit,
    kpt_path="Bi_nscf.in",
    command=f"{ABINIT_PATH} < Bi_nscf.files >& log",
    executable="/bin/bash",
)

# calculating the WCC
result_0 = z2pack.surface.run(
    system=Bi,
    surface=lambda s, t: [0, s / 2, t],
    save_file="./results/Bi_0.msgpack",
    load=True,
)
result_1 = z2pack.surface.run(
    system=Bi,
    surface=lambda s, t: [0.5, s / 2, t],
    save_file="./results/Bi_1.msgpack",
    load=True,
)
print(
    'Z2 topological invariant at kx = 0: {0}'.format(
        z2pack.invariant.z2(result_0)
    )
)
print(
    'Z2 topological invariant at kx = 0.5: {0}'.format(
        z2pack.invariant.z2(result_1)
    )
)
