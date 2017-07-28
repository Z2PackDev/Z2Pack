#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import scipy.linalg as la
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
        self.lines.add(SurfaceLine(t, result))

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
        if len(self.t) == 0:
            return 1
        return min(abs(t - tval) for tval in self.t)

    def nested_line(self, selector_fct=lambda ev, es: np.ones_like(ev, dtype=bool)):
        from ..line._data import EigenstateLineData
        selected_wilson_eigenstates = [
            [
                es_val for es_val, select in zip(es, selector_fct(ev, es))
                if select
            ]
            for ev, es in zip(self.wcc, self.wilson_eigenstates)
        ]
        wannier_band_states = [[
                es_wil_vec @ es_ham[0]
                for es_wil_vec in es_wil
            ]
            for es_wil, es_ham in zip(
                selected_wilson_eigenstates,
                self.eigenstates
            )
        ]
        wannier_band_states.append(wannier_band_states[0])
        return EigenstateLineData(eigenstates=wannier_band_states)

class SurfaceLine:
    __slots__ = ['t', 'result']

    def __init__(self, t, result):
        self.t = t
        self.result = result

    def __getattr__(self, key):
        if key not in ['t', 'result']:
            return getattr(self.result, key)
        return super().__getattribute__(key)
