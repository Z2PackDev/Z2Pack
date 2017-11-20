"""Tests for calculating invariants in symmetry eigenspaces for hm systems"""

import numpy as np
import z2pack

def test_projectors():
    hamilton = lambda k: [[np.sin(np.pi*k[1]), j], [-1.j, np.sin(np.pi*k[0])]]
    system = z2pack.hm.System(hamilton, dim=2)
