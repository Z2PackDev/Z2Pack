#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fsc.export import export
from fsc.locker import ConstLocker
from sortedcontainers import SortedList

@export
class VolumeData(metaclass=ConstLocker):
    """
    Data container for a volume calculation. It contains the :class:`.SurfaceResult` instances of all the surfaces in the volume which have been calculated.

    The following properties / attributes can be accessed:

    * ``pos`` : A tuple containing all current surface positions.
    * ``surfaces`` : A sorted list of objects which have two attributes ``pos`` (the position, which is the sorting key) and ``result`` (the surface's result).

    The attributes of the underlying :class:`.SurfaceResult` instances can be directly accessed from the :class:`.VolumeData` object. This will create a list of attributes for all surfaces, in the order of their position.

    """
    # cannot be pickled if it is a local method (lambda) in __init__
    # when python3.4 support is dropped, operator.attrgetter can be used
    @staticmethod
    def _sort_key(x):
        return x.pos

    def __init__(self, surfaces=()):
        self.surfaces = SortedList(surfaces, key=self._sort_key)

    def add_surface(self, pos, result):
        """Adds a surface result to the list of surfaces.

        :param pos:   Position of the surface.
        :type pos:    float

        :param result:  Result of the line calculation.
        :type result:   :class:`.LineResult`
        """
        self.surfaces.add(VolumeSurface(pos, result))

    def __getattr__(self, key):
        if key != 'surfaces':
            return [getattr(surface, key) for surface in self.surfaces]
        raise AttributeError

    @property
    def pos(self):
        return tuple(surface.pos for surface in self.surfaces)

    def nearest_neighbour_dist(self, pos):
        """
        Returns the distance between :math:`pos` and the nearest existing surface.
        """
        if len(self.pos) == 0:
            return 1
        return min(abs(pos - pval) for pval in self.pos)

class VolumeSurface:
    __slots__ = ['pos', 'result']

    def __init__(self, pos, result):
        self.pos = pos
        self.result = result

    def __getattr__(self, key):
        if key not in ['pos', 'result']:
            return getattr(self.result, key)
        return super().__getattribute__(key)
