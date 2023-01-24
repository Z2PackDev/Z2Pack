"""Defines the data containers for surface calculations."""

from fsc.export import export
from fsc.locker import ConstLocker
from sortedcontainers import SortedList


@export
class VolumeData(metaclass=ConstLocker):
    """
    Data container for a volume calculation. It contains the :class:`.SurfaceResult` instances of all the surfaces in the volume which have been calculated.

    The following properties / attributes can be accessed:

    * ``s`` : A tuple containing all current surface positions.
    * ``surfaces`` : A sorted list of objects which have two attributes ``s`` (the position, which is the sorting key) and ``result`` (the surface's result).

    The attributes of the underlying :class:`.SurfaceResult` instances can be directly accessed from the :class:`.VolumeData` object. This will create a list of attributes for all surfaces, in the order of their position.
    """

    # cannot be pickled if it is a local method (lambda) in __init__
    # when python3.4 support is dropped, operator.attrgetter can be used
    @staticmethod
    def _sort_key(x):
        return x.s

    def __init__(self, surfaces=()):
        self.surfaces = SortedList(surfaces, key=self._sort_key)

    def add_surface(self, s, result):
        """Adds a surface result to the list of surfaces.

        :param s:   Position of the surface.
        :type s:    float

        :param result:  Result of the surface calculation.
        :type result:   :class:`.SurfaceResult`
        """
        self.surfaces.add(SurfacePosition(s, result))

    def __getattr__(self, key):
        if key != "surfaces":
            return [getattr(surface, key) for surface in self.surfaces]
        raise AttributeError

    @property
    def s(self):
        return tuple(surface.s for surface in self.surfaces)

    def nearest_neighbour_dist(self, s):
        """
        Returns the distance between :math:`s` and the nearest existing surface.
        """
        if not self.s:
            return 1
        return min(abs(s - sval) for sval in self.s)


class SurfacePosition:
    """Wraps the surface result and its position in the volume."""

    __slots__ = ["s", "result"]

    def __init__(self, s, result):
        self.s = s
        self.result = result

    def __getattr__(self, key):
        if key not in ["s", "result"]:
            return getattr(self.result, key)
        return super().__getattribute__(key)
