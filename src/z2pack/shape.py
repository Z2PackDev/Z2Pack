#!/usr/bin/env python
"""
This module contains pre-defined shapes to use as the ``surface`` argument of :func:`.surface.run` or ``line`` argument for :func:`.line.run`, defining the shape of the surface or line.
"""

import numpy as np

__all__ = ["Sphere"]


class Sphere:
    r"""
    :param center:  Center of the sphere
    :type center:   list

    :param radius:  Radius of the sphere
    :type radius:   float


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
        return f"Sphere({self.center}, {self.radius})"

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
