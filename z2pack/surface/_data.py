"""Defines the data containers for surface calculations."""

from fsc.export import export
from fsc.locker import ConstLocker
from sortedcontainers import SortedList


@export
class SurfaceData(metaclass=ConstLocker):
    """
    Data container for a surface calculation. It contains the :class:`.LineResult` instances of all the lines on the surface which have been calculated.

    The following properties / attributes can be accessed:

    * ``t`` : A tuple containing all current line positions.
    * ``lines`` : A sorted list of objects which have two attributes ``t`` (the position, which is the sorting key) and ``result`` (the line's result).
    * ``symm_list``: A tuple containing all the symmetries of the surface as matrices in reduced coordinates.

    The attributes of the underlying :class:`.LineResult` instances can be directly accessed from the :class:`.SurfaceData` object. This will create a list of attributes for all lines, in the order of their position.

    """
    # cannot be pickled if it is a local method (lambda) in __init__
    # when python3.4 support is dropped, operator.attrgetter can be used
    @staticmethod
    def _sort_key(x):
        return x.t

    def __init__(self, lines=()):
        self.lines = SortedList(lines, key=self._sort_key)

    def add_line(self, t, result):
        """Adds a line result to the list of lines.

        :param t:   Position of the line (:math:`t_1`).
        :type t:    float

        :param result:  Result of the line calculation.
        :type result:   :class:`.LineResult`
        """
        self.lines.add(LinePosition(t, result))

    def __getattr__(self, key):
        if key != 'lines':
            return [getattr(line, key) for line in self.lines]
        raise AttributeError

    @property
    def t(self):
        return tuple(line.t for line in self.lines)

    def nearest_neighbour_dist(self, t):
        """
        Returns the distance between :math:`t` and the nearest existing line.
        """
        if not self.t:
            return 1
        return min(abs(t - tval) for tval in self.t)

    @property
    def symm_list(self):
        return self._symm_list

    @symm_list.setter
    def symm_list(self, s):
        self._symm_list = s

    def symm_project(self, eigval, isym=0):
        """
        Returns a new surface data object with everything projected onto one symmetry eigenspace.
        The lines of this surface data object are not LineResult objects, but OverlapLineData objects, i.e. they do not include convergence information.
        :param isym:    Index of symmetry that should be used for fp systems. List of symmetries with indices may be obtained by running surface.symm_list
        """
        lines = []
        for l in self.lines:
            #project the line onto the symmetry eigenspace
            l_new = LinePosition(l.t, l.symm_project(eigval, isym=isym))
            lines.append(l_new)
        lines = SortedList(lines, key=self._sort_key)
        return SurfaceData(lines)


class LinePosition:
    """Wraps the line result and its position in the surface."""
    __slots__ = ['t', 'result']

    def __init__(self, t, result):
        self.t = t
        self.result = result

    def __getattr__(self, key):
        if key not in ['t', 'result']:
            return getattr(self.result, key)
        return super().__getattribute__(key)
