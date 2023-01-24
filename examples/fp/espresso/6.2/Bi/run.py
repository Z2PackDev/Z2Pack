#!/usr/bin/env python

import os
import shutil
import subprocess
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import z2pack

# Edit the paths to your Quantum Espresso and Wannier90 here
qedir = "/home/greschd/software/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/quantum-espresso-6.6-hzv46p4wdlvw6rrgq3cqnz7fwwzd7um6/bin"
wandir = "/home/greschd/software/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/wannier90-3.1.0-ldgbc7e5fmfkvjiyf2xiyzfopyr5haqa/bin"

# Commands to run pw, pw2wannier90, wannier90
mpirun = "mpirun -np 4 "
pwcmd = mpirun + qedir + "/pw.x "
pw2wancmd = mpirun + qedir + "/pw2wannier90.x "
wancmd = wandir + "/wannier90.x"

z2cmd = (
    wancmd
    + " -pp bi;"
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
    kpt_fct=[z2pack.fp.kpoint.qe_explicit, z2pack.fp.kpoint.wannier90_full],
    kpt_path=["bi.nscf.in", "bi.win"],
    command=z2cmd,
    executable="/bin/bash",
    mmn_path="bi.mmn",
)

# Run the WCC calculations
result_0 = z2pack.surface.run(
    system=system,
    surface=lambda s, t: [0, s / 2, t],
    save_file="./results/res_0.json",
    min_neighbour_dist=1e-3,
    load=True,
)
result_1 = z2pack.surface.run(
    system=system,
    surface=lambda s, t: [0.5, s / 2, t],
    save_file="./results/res_1.json",
    min_neighbour_dist=1e-3,
    load=True,
)

# Combining the two plots
fig, ax = plt.subplots(1, 2, sharey=True, figsize=(9, 5))
z2pack.plot.wcc(result_0, axis=ax[0])
z2pack.plot.wcc(result_1, axis=ax[1])
plt.savefig("plots/plot.pdf", bbox_inches="tight")

print(f"Z2 topological invariant at kx = 0: {z2pack.invariant.z2(result_0)}")
print(f"Z2 topological invariant at kx = 0.5: {z2pack.invariant.z2(result_1)}")
