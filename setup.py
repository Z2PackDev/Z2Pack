"""Usage: pip install ."""

import re
from setuptools import setup, find_packages

import sys
if sys.version_info < (3, 6):
    raise 'must use Python version 3.6 or higher'

README = r"""Z2Pack is a tool that computes topological invariants and illustrates non-trivial features of Berry curvature. It works as a post-processing tool with all major first-principles codes (z2pack.fp), as well as with tight-binding models (z2pack.tb) and explicit Hamiltonian matrices -- such as the ones obtained from a k.p model (z2pack.hm).

It tracks the charge centers of hybrid Wannier functions - as described `here <http://journals.aps.org/prb/abstract/10.1103/PhysRevB.83.235401>`_ - to calculate these topological invariants.

The Wannier charge centers are computed from overlap matrices that are obtained either directly (for tb) or via the Wannier90 code package (fp).

`Documentation: <https://z2pack.greschd.ch>`_
"""

with open('./z2pack/__init__.py', 'r') as f:
    MATCH_EXPR = "__version__[^'\"]+(['\"])([^'\"]+)"
    VERSION = re.search(MATCH_EXPR, f.read()).group(2).strip()

EXTRAS = {
    'plot': ['matplotlib'],
    'tb': ['tbmodels>=1.1.1'],
    'doc': ['sphinx', 'sphinx-rtd-theme', 'sphinx-pyreverse', 'pylint==2.4.4'],
    'dev':
    ['pytest~=6.0', 'pytest-cov', 'yapf==0.29', 'pre-commit', 'pylint==2.4.4'],
}
EXTRAS['dev'] += EXTRAS['plot'] + EXTRAS['tb'] + EXTRAS['doc']

setup(
    name='z2pack',
    version=VERSION,
    url='https://z2pack.greschd.ch',
    author='Dominik Gresch',
    author_email='greschd@gmx.ch',
    description=
    'Automating the computation of topological numbers of band-structures',
    install_requires=[
        'numpy', 'scipy', 'decorator', 'blessings', 'sortedcontainers',
        'msgpack-python', 'fsc.locker', 'fsc.export', 'fsc.formatting',
        'fsc.iohelper'
    ],
    extras_require=EXTRAS,
    python_requires=">=3.6",
    long_description=README,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English', 'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Development Status :: 5 - Production/Stable'
    ],
    license='GPL',
    keywords=[
        'topology', 'topological', 'invariant', 'bandstructure', 'chern', 'z2',
        'solid-state', 'tight-binding'
    ],
    packages=find_packages()
)
