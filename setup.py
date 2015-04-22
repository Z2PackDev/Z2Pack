#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.10.2014 11:27:40 CEST
# File:    setup.py

import re
try:
    from setuptools import setup
except:
    from distutils.core import setup

readme = r"""Z2Pack is a tool for calculating topological invariants on
first-principles (z2pack.fp) and tight-binding (z2pack.tb) systems.

It uses the method described in http://journals.aps.org/prb/abstract/10.1103/PhysRevB.83.235401
to calculate the Z2 topological invariant.

Overlap matrices are calculated either directly (for tb) or via
the Wannier90 code package (fp).

- Documentation: http://z2pack.ethz.ch/doc
- Online interface: http://z2pack.ethz.ch/online
"""

with open('./z2pack/_version.py', 'r') as f:
    match_expr = "__version__[^'" + '"]+([' + "'" + r'"])([^\1]+)\1'
    version = re.search(match_expr, f.read()).group(2)

setup(
    name='z2pack',
    version=version,
    url='http://z2pack.ethz.ch',
    author='Dominik Gresch',
    author_email='greschd@gmx.ch',
    description='A tool for computing topological invariants',
    install_requires=['numpy', 'scipy', 'decorator'],
    extras_require = {'plot':  ['matplotlib']},
    long_description=readme,
    license='LICENSE.txt',
    packages=['z2pack',
              'z2pack.ptools',
              'z2pack.tb',
              'z2pack.fp'])
