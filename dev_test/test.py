#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.06.2015 08:51:02 CEST
# File:    test.py

import sys
sys.path.insert(0, '../')
import z2pack

import numpy as np
import scipy.linalg as la
from ptools.plot_setup import *
use_style('plain')

t1, t2 = (0.2, 0.3)
on_site = [1, 1, -1, -1]
hoppings = [[0, 2, [0, 0, 0], t1],
            [0, 2, [-1, 0, 0], t1 * (-1j)],
            [0, 2, [-1, -1, 0], t1 * (-1)],
            [0, 2, [0, -1, 0], t1 * (1j)],
            [1, 3, [0, 0, 0], t1],
            [1, 3, [-1, 0, 0], t1 * (1j)],
            [1, 3, [-1, -1, 0], t1 * (-1)],
            [1, 3, [0, -1, 0], t1 * (-1j)],
            [0, 0, [1, 0, 0], t2],
            [0, 0, [0, 1, 0], t2],
            [1, 1, [1, 0, 0], t2],
            [1, 1, [0, 1, 0], t2],
            [2, 2, [1, 0, 0], -t2],
            [2, 2, [0, 1, 0], -t2],
            [3, 3, [1, 0, 0], -t2],
            [3, 3, [0, 1, 0], -t2]]
            
positions = [[0., 0., 0.], [0., 0., 0.], [0.5, 0.5, 0.], [0.5, 0.5, 0.]]
model = z2pack.em.tb.Model(on_site, hoppings, positions, occ=2)

k = [[kval, 0.5, 0.] for kval in np.linspace(0, 1, 101)]
eig = []
for kval in k:
    eig.append(sorted(la.eigh(model.hamilton(kval))[0]))

bands = np.array(eig).T
for band in bands:
    plt.plot(k, band)
plt.savefig('./plot.pdf', bbox_inches='tight')

if __name__ == "__main__":
    print("test.py")
    
