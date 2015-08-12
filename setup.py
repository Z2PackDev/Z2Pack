#!/usr/bin/env python
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

import sys
if sys.version_info < (2, 5):
    raise 'must use Python version 2.6 or higher, or 3.x'

readme = r"""Z2Pack is a tool that computes topological invariants and illustrates non-trivial features of Berry curvature. It works as a post-processing tool with all major first-principles codes (z2pack.fp), as well as with tight-binding models (z2pack.tb). 

It tracks the charge centers of hybrid Wannier functions - as described `here <http://journals.aps.org/prb/abstract/10.1103/PhysRevB.83.235401>`_ - to calculate these topological invariants.

The Wannier charge centers are computed from overlap matrices that are obtained either directly (for tb) or via the Wannier90 code package (fp).

- `Documentation <http://z2pack.ethz.ch/doc>`_
- `Online interface <http://z2pack.ethz.ch/online>`_ (tight-binding only)
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
    description='Automating the computation of topological numbers of band-structures',
    install_requires=['numpy', 'scipy', 'decorator'],
    extras_require = {'plot':  ['matplotlib']},
    long_description=readme,
    classifiers=['License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Natural Language :: English',
                 'Operating System :: Unix',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering :: Physics'],
    license='GPL',
    packages=['z2pack',
              'z2pack.ptools',
              'z2pack.tb',
              'z2pack.fp'])
