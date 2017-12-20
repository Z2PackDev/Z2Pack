#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains a class describing a surface in the reduced Brillouin zone."""

from fsc.export import export


@export
class ReducedSurface:
    """
    This class describes a surface in the Brillouin zone in reduced coordinates.
    The following properties can be accessed:

    * ``vectors``: Tuple of three vectors: The first vector defines the origin of the surface, the other two vectors span the surface. Every point on the surface can be expressed as ``vectors[0] + s*vectors[1] + t*vectors[2]``.
    * ``surface_lambda``: A function describing the surface, to be used for a surface run.
    * ``symm``: Symmetry matrix under which every point on the surface is invariant.

    """

    def __init__(self, *, vectors=None, surface_lambda=None, symm=None):
        r"""
        :param vectors:  Tuple of three vectors: The first vector defines the origin of the surface, the other two vectors span the surface. Every point on the surface can be expressed as ``vectors[0] + s*vectors[1] + t*vectors[2]``.
        :type vectors:   list

        :param surface_lambda: A function of the kind used for the ``surface`` argument in surface runs.
        :type surf_lambda:  function

        :param symm:    (optional) Symmetry matrix under which every point on the surface is invariant.
        :type symm:     :py:class:`numpy.ndarray`

        """
        if vectors is not None:
            #create surface based on vectors
            if len(vectors) != 3:
                raise ValueError(
                    "Surface has to be specified by three vectors: one giving its origin and two for spanning the surface."
                )
            self._vectors = vectors
            self._surf_lambda = self._lambda_from_vec()

        elif surface_lambda is not None:
            #create surface based on lambda function
            self._surf_lambda = surface_lambda
            self._vectors = self._vec_from_lambda()
        else:
            raise ValueError("Surface cannot be unspecified.")
        self._symm = symm

    @property
    def vectors(self):
        return self._vectors

    @property
    def surface_lambda(self):
        return self._surf_lambda

    @property
    def symm(self):
        return self._symm

    def _lambda_from_vec(self):
        return lambda s, t: self._vectors[0] + s * self._vectors[1] + t * self._vectors[2]

    def _vec_from_lambda(self):
        return [
            self._surf_lambda(0, 0),
            self._surf_lambda(1, 0),
            self._surf_lambda(0, 1)
        ]
