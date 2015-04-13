#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    12.04.2015 19:58:32 CEST
# File:    shapes.py

"""
A collection of pre-defined shapes to use as the ``param_fct`` argument
of :meth:`.surface()`, defining the shape of the surface.
"""

import numpy as np

class Sphere:
    r"""
    :param center:  Center of the sphere
    :type center:   list

    :param radius:  Radius of the sphere
    :type radius:   float
    """
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __call__(self, t, k):
        """
        t - theta (angle along z)
        k - phi (angle in z=0 plane)
        """
        x, y, z = self.center
        x += self.radius * np.cos(2 * np.pi * k) * np.sin(np.pi * t)
        y += self.radius * np.sin(2 * np.pi * k) * np.sin(np.pi * t)
        z -= self.radius * np.cos(np.pi * t)
        return [x, y, z]
