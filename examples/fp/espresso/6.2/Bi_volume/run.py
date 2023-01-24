#!/usr/bin/env python

import os
import shutil
import subprocess
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt

import z2pack

# Edit the paths to your Quantum Espresso and Wannier90 here
qedir = "/home/greschd/software/qe-6.2/bin"
wandir = "/home/greschd/software/wannier90-2.1.0"

# Commands to run pw, pw2wannier90, wannier90
mpirun = "mpirun -np 4 "
pwcmd = mpirun + qedir + "/pw.x "
pw2wancmd = mpirun + qedir + "/pw2wannier90.x "
wancmd = wandir + "/wannier90.x"

z2cmd = (
    wancmd
    + " bi -pp;"
    + pwcmd
    + "< bi.nscf.in >& pw.log;"
    + pw2wancmd
    + "< bi.pw2wan.in >& pw2wan.log;"
)

# creating the results folder, running the SCF calculation if needed
if not os.path.exists("./plots"):
    os.mkdir("./plots")
if not os.path.exists("./results"):
    os.mkdir("./results")
if not os.path.exists("./scf"):
    os.makedirs("./scf")
    print("Running the scf calculation")
    shutil.copyfile("input/bi.scf.in", "scf/bi.scf.in")
    subprocess.call(pwcmd + " < bi.scf.in > scf.out", shell=True, cwd="./scf")

# Copying the lattice parameters from bi.save/data-file.xml into bi.win
cell = ET.parse("scf/bi.xml").find("output").find("atomic_structure").find("cell")
unit = cell.get("unit", "Bohr")
lattice = "\n".join([cell.find(vec).text for vec in ["a1", "a2", "a3"]])

with open("input/tpl_bi.win") as f:
    tpl_bi_win = f.read()
with open("input/bi.win", "w") as f:
    f.write(tpl_bi_win.format(unit=unit, lattice=lattice))

# Creating the System. Note that the SCF charge file does not need to be
# copied, but instead can be referenced in the .files file.
# The k-points input is appended to the .in file
input_files = ["input/" + name for name in ["bi.nscf.in", "bi.pw2wan.in", "bi.win"]]
system = z2pack.fp.System(
    input_files=input_files,
    kpt_fct=[z2pack.fp.kpoint.qe, z2pack.fp.kpoint.wannier90_full],
    kpt_path=["bi.nscf.in", "bi.win"],
    command=z2cmd,
    executable="/bin/bash",
    mmn_path="bi.mmn",
)

# Run the WCC calculations
result = z2pack.volume.run(
    system=system,
    volume=lambda t1, t2, t3: [t1 / 2, t2 / 2, t3],
    save_file="./results/res.json",
    load=True,
)

fig = z2pack.plot.wcc_3d(result)
plt.show()
