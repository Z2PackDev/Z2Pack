#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains pre-defined shapes to use as the ``surface`` argument of :func:`.surface.run` or ``line`` argument for :func:`.line.run`, defining the shape of the surface or line.
"""

import numpy as np
from fsc.export import export


@export
class Sphere:
    r"""
    Arguments
    ---------
    center : list
        Center of the sphere
    radius : float
        Radius of the sphere

    Example usage:

    .. code :: python

        z2pack.surface.run(
            system=..., # Refer to the various ways of defining a system.
            surface=z2pack.shape.Sphere(center=[0, 0, 0], radius=0.1)
        )
    """
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __str__(self):
        return 'Sphere({}, {})'.format(self.center, self.radius)

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


@export
class Plane:
    r"""
    This class describes a plane in the Brillouin zone in reduced coordinates.
    The plane defines a surface

    .. math::

        f(s, t) = ``origin`` + s \cdot ``spanning_vectors[0]`` + t \cdot ``spanning_vectors[1]``

    Arguments
    ---------
    origin : numpy.ndarray
        A vector defining the origin / offset of the plane.
    spanning_vectors : list
        List of two vectors which span the plane.
    """
    def __init__(self, *, origin, spanning_vectors):
        #create surface based on vectors
        self._origin = np.array(origin)
        self._spanning_vectors = list(
            np.array(vec) for vec in spanning_vectors
        )
        if len(self._spanning_vectors) != 2:
            raise ValueError('Exactly two spanning vectors must be given.')

    def __str__(self):
        return 'Plane(origin={}, spanning_vectors={})'.format(
            self._origin, self._spanning_vectors
        )

    def __call__(self, s, t):
        return self._origin + s * self._spanning_vectors[
            0] + t * self._spanning_vectors[1]
