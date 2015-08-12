#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    22.09.2014 14:23:12 CEST
# File:    squarelattice.py

import sys
import matplotlib
#~ sys.path.append("/home/autes/Progs/Z2Pack-master/")
import matplotlib.pyplot as plt

sys.path.insert(0, '../')
import z2pack.tb as tb
import scipy.linalg as la
import numpy as np
from numpy import cos, sin, pi, exp

from ptools.plot_setup import *
plot_style(cmbright=True)
#~ from cmath import exp

def tci_h(k):
  kx=k[0]*2*pi
  ky=k[1]*2*pi
  kz=k[2]*2*pi
  t1a, t1b, t2a , t2b, t1,t2, tz  = (1.0, -1.0 , 0.5 , -0.5 ,2.5 , 0.5 , 2.0 )
  H=np.matrix( [[ 2*t1a*cos(kx) + 2*t2a*cos(kx)*cos(ky)   , 2*t2a*sin(kx)*sin(ky)                   , t1+2*t2*(cos(kx)+cos(ky))+tz*exp(1j*kz), 0                                       ],
                [ 2*t2a*sin(kx)*sin(ky)                   , 2*t1a*cos(kx) + 2*t2a*cos(kx)*cos(ky)   , 0                                      , t1+2*t2*(cos(kx)+cos(ky))+tz*exp(1j*kz) ],
                [ t1+2*t2*(cos(kx)+cos(ky))+tz*exp(-1j*kz), 0                                       , 2*t1b*cos(kx) + 2*t2b*cos(kx)*cos(ky)  , 2*t2b*sin(kx)*sin(ky)                   ],
                [ 0                                       , t1+2*t2*(cos(kx)+cos(ky))+tz*exp(-1j*kz), 2*t2b*sin(kx)*sin(ky)                  , 2*t1b*cos(kx) + 2*t2b*cos(kx)*cos(ky)   ]], dtype=complex)
  return H


# Setting the interaction strength
#t1, t2 = (0.2, 0.3)

# Settings used for wcc_calc. Feel free to play around with the different
# options.
settings = {'num_strings': 41,
            'pos_tol': 1e-3,
            'gap_tol': 2e-3,
            'move_tol': 0.3,
            'iterator': range(20, 50, 2),
            'min_neighbour_dist': 1e-4,
            'pickle_file': 'res_pickle.txt',
            'verbose': True
           }

# Creating an empty Hamilton instance
H = tb.Hamilton()

# Creating the two atoms. The orbitals have opposite energies because
# they are in different sublattices.
H.add_atom(([0, 0], 1), [0, 0, 0])
H.add_atom(([0, 0], 1), [0, 0, 0.5])
H.create_hamiltonian()
H.hamiltonian=tci_h


# plot band structure
ek=[]
# Gamma M
for i in range(0,100):
  k=(0.5*i/100,0.5*i/100,0)
  eigval,eigvec = la.eig(tci_h(k))
  ek.append([float(e) for e in eigval]) 
# M A
for i in range(0,100):
  k=(0.5,0.5,0.5*i/100)
  eigval,eigvec = la.eig(tci_h(k))
  ek.append([float(e) for e in eigval]) 
# A Z
for i in range(0,100):
  k=(0.5-0.5*i/100,0.5-0.5*i/100,0.5)
  eigval,eigvec = la.eig(tci_h(k))
  ek.append([float(e) for e in eigval]) 
# Z M
for i in range(0,100):
  k=(0.0,0.0,0.5-0.5*i/100)
  eigval,eigvec = la.eig(tci_h(k))
  ek.append([float(e) for e in eigval]) 

out=open('bands.dat','w')
ik=0
for eig in ek:
   eig.sort()
   ik+=1
   print >> out ,ik,eig[0]
ik=0
print >> out ," "
for eig in ek:
   eig.sort()
   ik+=1
   print >> out, ik,eig[1]

ik=0
print >> out, " "
for eig in ek:
   eig.sort()
   ik+=1
   print >> out,ik,eig[2]
ik=0
print >> out ," "
for eig in ek:
   eig.sort()
   ik+=1
   print >> out,ik,eig[3]
  
  
  
  

# Creating the System
tb_system = tb.System(H)


font = {'family' : 'normal',
          'weight' : 'normal',
          'size'   : 8}
plt.rc('font', **font)
plt.rc('lines', markersize=3)
fig=plt.figure()

ax=fig.add_subplot(1,3,1)
ax.set_title("plane kx=0 - string along kz")
tb_surface = tb_system.surface(lambda kx: [0.0 , kx/2.0 , 0.0], [0, 0, 1])
tb_surface.wcc_calc(**settings)
tb_surface.plot(show=False,axis=ax)


ax=fig.add_subplot(1,3,2)
ax.set_title("plane ky=0.5 - string along kz")
tb_surface = tb_system.surface(lambda kx: [kx/2 , 0.5, 0.0], [0, 0, 1])
tb_surface.wcc_calc(**settings)
tb_surface.plot(show=False,axis=ax)

ax=fig.add_subplot(1,3,3)
ax.set_title("plane ky=kx - string along kz")
tb_surface = tb_system.surface(lambda kx: [0.5-kx/2.0 , 0.5-kx/2.0, 0.0], [0, 0, 1])
tb_surface.wcc_calc(**settings)
tb_surface.plot(show=False,axis=ax)


plt.savefig('wcc.pdf',bbox_inches='tight')

# Printing the results
#print("t1: {0}, t2: {1}, Z2 invariant: {2}".format(t1, t2, tb_surface.invariant()))

