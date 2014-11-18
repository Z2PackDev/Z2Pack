#!/usr/bin/python3
#
# File:    bi_qe.py
#
#################################################################
#
# Set to false if you don't want to plot the figure
#
plotfig=True
#
# Edit here the path to QE, wannier90 and z2pack
#
z2dir="/home/autes/Progs/z2pack/z2pack-0.1"
qedir="/home/autes/Progs/espresso-5.1_wanlib/espresso-5.1/bin"
wandir="/home/autes/Progs/z2pack/z2pack-0.1/Wannier90/wannier90-1.2.0.1"
#
# Edit here the command to run pw.x, pw2wannier90.x and wannier90.x 
#
mpirun="/usr/lib64/mpich2/bin/mpirun -np 4 "
pwcmd=mpirun+qedir+"/pw.x " 
pw2wancmd=mpirun+qedir+"/pw2wannier90.x "
wancmd=wandir+"/wannier90.x"
# Edit here the command that z2pack should run to produce the .mmn file
z2cmd=wancmd+" bi -pp;"+pwcmd+"< bi.nscf.in >& pw.log;"+pw2wancmd+"< bi.pw2wan.in >& pw2wan.log;"
################################################################
#
# import
#
import os
import sys
if(plotfig):
  import matplotlib.pyplot as plt
sys.path.append(z2dir)
import z2pack
#
# create the results and scf directories 
#
if not os.path.exists('./results'):
    os.makedirs('./results')
if not os.path.exists('./scf'):
    os.makedirs('./scf')
#
# run the scf calculation
#
print("Running the scf calculation")
os.chdir('./scf')
os.system('cp ../bi.scf.in ./')
os.system(pwcmd+" < bi.scf.in > scf.out")
os.chdir('../')
#
# creating the z2pack.qe object
#
Bi = z2pack.fp.System(  ["bi.nscf.in", "bi.pw2wan.in", "bi.win" ],       # input files needed to create the bi.mmn file
                        [z2pack.fp.kpts.qe,z2pack.fp.kpts.wannier90],    # fonctions which return the kpoint path string in qe and wannier90 format
                        ["bi.nscf.in","bi.win"],                         # input files where the kpoint path string is added
                        "build",                                         # working directory
                        z2cmd,                                           # command to run to produce the bi.mmn file
                        executable='/bin/bash',                          #
                        mmn_path='bi.mmn'                                # 
                    )
if(plotfig):    
  fig=plt.figure()
#
# define plane with strings along k1 and k2=0.0
#
print("Computing the Z2 invariant for strings along k1 and k2=0.0") 
Bi_plane = Bi.plane(0,1,0.0, pickle_file = 'results/res1.txt')
#
# compute the wannier centers
#
Bi_plane.wcc_calc(no_iter = True, no_neighbour_check = False)
#
# plot the results
#
if(plotfig):
  ax=fig.add_subplot(1,2,1)
  Bi_plane.plot(show= False, axis = ax)
#
# compute the invariant
#
print("Z2 invariant: {0}".format( Bi_plane.invariant()))

#
# define plane with strings along k1 and k2=0.5
#
print("Computing the Z2 invariant for strings along k1 and k2=0.5") 
Bi_plane = Bi.plane(0,1,0.5, pickle_file = 'results/res2.txt')
#
# compute the wannier centers
#
Bi_plane.wcc_calc(no_iter = True, no_neighbour_check = False)
#
# plot the results
#
if(plotfig):
  ax=fig.add_subplot(1,2,2)
  Bi_plane.plot(show= False, axis = ax)
#
# compute the invariant
#
print("Z2 invariant: {0}".format( Bi_plane.invariant()))



if(plotfig):
  plt.savefig('bi.pdf', bbox_inches = 'tight') 
################################################################






