"""
Defines fixtures for local paths needed for first-principles runs.
"""

import os
import yaml
import pytest

try:
    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'local_config.yml'
        ), 'r'
    ) as f:
        CONFIG = yaml.load(f)
except IOError:
    CONFIG = dict()


@pytest.fixture
def qe_5_4_dir():
    return CONFIG['qe_5_4_dir']


@pytest.fixture
def qe_6_0_dir():
    return CONFIG['qe_6_0_dir']


@pytest.fixture
def qe_6_2_dir():
    return CONFIG['qe_6_2_dir']


@pytest.fixture
def wannier_2_1_dir():
    return CONFIG['wannier_2_1_dir']
