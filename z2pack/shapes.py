#!/usr/bin/env python
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

class SimpleEllipsoid(object):
    r"""
    An ellipsoid whose symmetry axes correspond to :math:`k_x, k_y, k_z`.
    
    :param center:  Center of the ellipsoid
    :type center:   list

    :param ax:  Semi-principal axis along :math:`k_x`
    :type ax:   float

    :param ay:  Semi-principal axis along :math:`k_y`
    :type ay:   float

    :param az:  Semi-principal axis along :math`k_z`
    :type az:   float
    """
    def __init__(self, center, ax, ay, az):
        self.center = center
        self.ax = ax
        self.ay = ay
        self.az = az

    def __call__(self, t, k):
        """
        t - theta (angle along z)
        k - phi (angle in z=0 plane)
        """
        x, y, z = self.center
        x += self.ax * np.cos(2 * np.pi * k) * np.sin(np.pi * t)
        y += self.ay * np.sin(2 * np.pi * k) * np.sin(np.pi * t)
        z -= self.az * np.cos(np.pi * t)
        return [x, y, z]

class Sphere(SimpleEllipsoid):
    r"""
    :param center:  Center of the sphere
    :type center:   list

    :param radius:  Radius of the sphere
    :type radius:   float
    """
    def __init__(self, center, radius):
        super(Sphere, self).__init__(center, radius, radius, radius)

