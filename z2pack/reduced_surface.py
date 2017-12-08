"""Helper class for surfaces. Mostly used to convert between vector and lambda representation of surface."""

import numpy as np
from fsc.export import export

@export
class ReducedSurface:

    def __init__(self, *, vectors=None, surf_lambda=None):
        """
        vectors: tuple of three vectors. First element gives origin of surface, other two specify directions.
        """
        if vectors is not None:
            #create surface based on vectors
            if len(vectors) != 3:
                raise ValueError("Surface has to be specified by three vectors: one giving its origin and two for spanning the surface.")
            self._vectors = vectors
            self._surf_lambda = self._lambda_from_vec()

        elif surf_lambda is not None:
            #create surface based on lambda function
            self._surf_lambda = surf_lambda
            self._vectors = self._vec_from_lambda()
        else:
            raise ValueError("Surface cannot be unspecified.")

    @property
    def get_vectors(self):
        return self._vectors

    @property
    def get_lambda(self):
        return self._lambda

    def _lambda_from_vec(self):
        return lambda s, t: self._vectors[0] + s*self._vectors[1] + t*self._vectors[2]
        

    def _vec_from_lambda(self):
        return [self._surf_lambda(0, 0), self._surf_lambda(1, 0), self._surf_lambda(0, 1)]
