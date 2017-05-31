#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import matplotlib.pyplot as plt

import z2pack

result_0 = z2pack.io.load('results/Bi_0.msgpack')
result_1 = z2pack.io.load('results/Bi_1.msgpack')

# plotting
fig, ax = plt.subplots(1, 2)

# plot styling
fs = 15
for axis in ax:
    axis.set_xlabel(r'$k_y$', fontsize=fs)
    axis.set_xticks([0, 1])
    axis.set_xticklabels([r'$0$', r'$\pi$'])
ax[0].set_ylabel(r'$\bar{x}$', rotation='horizontal', fontsize=fs)
ax[0].set_title(
    r'$k_x=0, \Delta={}$'.format(z2pack.invariant.z2(result_0)),
    fontsize=fs
)
ax[1].set_title(
    r'$k_x=0, \Delta={}$'.format(z2pack.invariant.z2(result_1)),
    fontsize=fs
)

# plotting the WCC evolution
z2pack.plot.wcc(result_0, axis=ax[0])
z2pack.plot.wcc(result_1, axis=ax[1])

if not os.path.isdir('plots'):
    os.mkdir('plots')

plt.savefig('plots/plot.pdf', bbox_inches='tight')
