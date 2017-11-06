#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import itertools

import z2pack
import tbmodels
import matplotlib.pyplot as plt

logging.getLogger('z2pack').setLevel(logging.WARNING)

t1, t2 = (0.2, 0.3)

settings = {
    'num_lines': 11,
    'pos_tol': 1e-2,
    'gap_tol': 2e-2,
    'move_tol': 0.3,
    'iterator': range(8, 27, 2),
    'min_neighbour_dist': 1e-2,
}

model = tbmodels.Model(
    on_site=(1, 1, -1, -1),
    pos=[[0., 0., 0.], [0., 0., 0.], [0.5, 0.5, 0.], [0.5, 0.5, 0.]],
    occ=2
)

for p, R in zip([1, 1j, -1j, -1], itertools.product([0, -1], [0, -1], [0])):
    model.add_hop(overlap=p * t1, orbital_1=0, orbital_2=2, R=R)
    model.add_hop(overlap=p.conjugate() * t1, orbital_1=1, orbital_2=3, R=R)

for R in ((r[0], r[1], 0) for r in itertools.permutations([0, 1])):
    model.add_hop(t2, 0, 0, R)
    model.add_hop(t2, 1, 1, R)
    model.add_hop(-t2, 2, 2, R)
    model.add_hop(-t2, 3, 3, R)

tb_system = z2pack.tb.System(model)

result = z2pack.surface.run(
    system=tb_system, surface=lambda s, t: [s / 2., t, 0], **settings
)

fig, ax = plt.subplots()
z2pack.plot.wcc(result, axis=ax)
plt.savefig('plots/wcc.pdf', bbox_inches='tight')

print(
    "t1: {0}, t2: {1}, Z2 invariant: {2}".format(
        t1, t2, z2pack.invariant.z2(result)
    )
)
