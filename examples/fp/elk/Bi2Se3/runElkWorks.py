# -*- coding: utf-8 -*-

import os
import shutil
import subprocess

import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import numpy as np
import z2pack

def wannier90_nnkpts(kpt):
    """
    Creates the nnkpts input to explicitly specify the nearest neighbours in wannier90.win
    """
    N = len(kpt) - 1
    bz_diff = [np.zeros(3, dtype=int) for _ in range(N - 1)]
    # check whether the last k-point is in a different UC
    bz_diff.append(np.array(np.round_(kpt[-1] - kpt[0]), dtype=int))
    string = 'begin nnkpts\n'
    for i, k in enumerate(bz_diff):
        j = (i + 1) % N
        string += ' {0:>3} {1:>3}    {2[0]: } {2[1]: } {2[2]: }\n'.format(i + 1, j + 1, k)
    string += 'end nnkpts\n'
    return string


def _check_equal_spacing(kpt, run_type):
    """checks if the k-points are equally spaced, and throws an error if not. run_type is added in the error message"""
    deltas=[(k2-k1) % 1 for k2, k1 in zip(kpt[1:], kpt[:-1])]
    for d in deltas[1:]:
        if not np.isclose(d, deltas[0]).all():
            raise ValueError('The k-points must be equally spaced for {} runs.'.format(run_type))
    return deltas[0]

def kpt_elk(kpt):
    delta=_check_equal_spacing(kpt, 'ELK')
    N=len(kpt)-1
    #check if it's positive x, y, or z direction
    nonzero=[]
    mesh=[]
    for i, d in enumerate(delta):
        if np.isclose(d, 0):
            mesh.append('1')
        elif np.isclose(d, 1/N):
            nonzero.append(i)
            mesh.append(str(N))
        else:
            raise ValueError('The k-points must be aligned in (positive) kx-, ky- or kz-direction for ELK runs.')
    mesh_str = ' '.join(mesh)
    
    if len(nonzero) !=1:
        raise ValueError('The k-points can only change in kx-, ky-, or kz direction for ELK runs. The given k-points change in {} directions.'.format(len(nonzero)))

    s=wannier90_nnkpts(kpt)
    #s=''
    start_point=kpt[0]
    last_point=kpt[-2]
    if not np.isclose(start_point[nonzero[0]], 0):
        raise ValueError('The k-points must start at k{0} = 0 for ELK runs, since they change in k{0}-direction.'.format(['x', 'y', 'z'][nonzero[0]]))
    string=s+'\n\nngridk\n'+'1 1 '+str(N)+ '\n\n'
    #correct for 
    string+='vkloff\n'
    for coord in start_point:
        string+=str(coord).replace('e', 'd')+ ' '
    string+='\n\nplot1d\n2 '+str(N)+'\n'
    for coord in start_point:
        string+=str(coord).replace('e', 'd')+' '
    string+='\n'
    for coord in last_point:
        string+=str(coord).replace('e', 'd')+' '
    string+='\n'
    return string
    
# Edit the paths to your Elk and Wannier90 here
elkdir = '$HOME/Z2pack/elk-6.8.4/src/elk'



#I started only with elk.in in the inputs. In the QE tutorial, it started with tpl_bi.win also, copying the units and lattice to them, as well as the number of wannier bands

#first Wannierize data, next run nscf/bands calculation, next convert to Wannier
#in elk.in have both the bands calculation (20) and elk2wannier 550



# creating the results folder, running the SCF calculation if needed
if not os.path.exists('./plots'):
    os.mkdir('./plots')
if not os.path.exists('./results'):
    os.mkdir('./results')
if not os.path.exists('./ground'):
    os.makedirs('./ground')
    print("Running the ground state calculation")    
    #copy all scf calc *.OUT files to wannBands folder, generate initial wannier90 files (*.win, *.mmn, 
    shutil.copyfile('input/elkSCFwann.in', 'ground/elk.in')
    subprocess.call(elkdir + ' >& elkWannier.log', shell=True, cwd='./ground')

#%%Initial SCF calculation has run in the *.input directory


# Creating the System. Note that the SCF charge file does not need to be
# copied, but instead can be referenced in the .files file.
# The k-points input is appended to the .in file. I am not entirely sure which files are absolutely necessary so this is an exhaustive list.
input_files = [    'ground/' + name for name in ["elk.in","STATE.OUT", "INFO.OUT", "GEOMETRY.OUT", "LINENGY.OUT", "DTOTENERGY.OUT", "EFERMI.OUT","EIGVAL.OUT", "EQATOMS.OUT", "EVALCORE.OUT", "EVALFV.OUT", "EVALSV.OUT","EVECFV.OUT","EVECSV.OUT", "FERMIDOS.OUT", "GAP.OUT", "GEOMETRY.OUT", "IADIST.OUT", "LATTICE.OUT","KPOINTS.OUT", "MOMENT.OUT", "MOMENTM.OUT","OCCSV.OUT","RMSDVS.OUT","SYMCRYS.OUT", "SYMLAT.OUT", "SYMSITE.OUT","TOTENERGY.OUT"]]
#input_files.append('input/wannier.win')

#note that this ensures that elkWannBands.in is used rather than what was used for the *.scf calculation. These all end up showing up in the Buid directory
shutil.copyfile('input/elkWannBands.in', 'ground/elk.in')
system = z2pack.fp.System(
    input_files=input_files,
    kpt_fct=kpt_elk,
    kpt_path="elk.in",
    command='/home-2/epogue1@jhu.edu/Z2pack/elk-6.8.4/src/elk >& elk.log',
    mmn_path='wannier.mmn'
)

# Run the WCC calculations
result_0 = z2pack.surface.run(
    system=system,
    surface=lambda s, t: [0, s / 2, t],
    save_file='./results/res_0.json',
    load=True
)

print(
    'Z2 topological invariant at kx = 0: {0}'.format(
        z2pack.invariant.z2(result_0)
    )
)

# Plot the WCC
fig, ax = plt.subplots(1, 1, sharey=True, figsize=(9, 5))
z2pack.plot.wcc(result_0, axis=ax)
plt.savefig('plots/plot.pdf', bbox_inches='tight')


