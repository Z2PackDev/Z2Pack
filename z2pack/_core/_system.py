#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.06.2015 12:03:43 CEST
# File:    _system.py


from ._line import Line
from ._surface import Surface

import warnings
import numpy as np

class System(object):
    r"""
    Describes the interface a Z2Pack specialisation must fulfil. Also, it
    defines the :meth:`surface` method, which is used to create :class:`Surface`
    instances.

    :param m_handle: Creates the overlap matrices M given a list of k-points including the end point.
    :type m_handle: function
    """
    # TODO when all systems are new-style_remove (keyword RM_V2)
    _new_style_system = False

    def __init__(self, m_handle):
        self._m_handle = m_handle

    def surface(self, param_fct, string_vec=None, **kwargs):
        r"""
        Creates a :class:`Surface` instance. For a detailed
        description consult the :ref:`Tutorial <creating-surface>`.

        :param param_fct: Parametrizes either the full surface
            (``string_vec == None``) or its edge (``string_vec != None``),
            with the parameter going from :math:`0` to :math:`1`.
        :type param_fct: function
    
        :param string_vec: Direction of the individual k-point strings,
            if ``param_fct`` only parametrizes the edge of the surface.
            Note that ``string_vec`` must connect equivalent k-points
            (i.e. it must be a reciprocal lattice vector). Typically,
            it is one of ``[1, 0, 0]``, ``[0, 1, 0]``, ``[0, 0, 1]``.
        :type string_vec: list

        :param kwargs: Keyword arguments are passed to the :class:`Surface`
            constructor. They take precedence over kwargs from the
            :class:`System` constructor.

        :rtype: :class:`Surface`

        .. note:: All directions / positions are given w.r.t. the
            inverse lattice vectors.
        """
        # RM_V2
        if self._new_style_system:
            if string_vec is not None:
                warnings.warn('The parameter string_vec is soon to be ' +
                    'deprecated and will be removed when all System ' +
                    'classes support arbitrary surfaces.', DeprecationWarning, stacklevel=2)
        else:
            if string_vec is None:
                warnings.warn('This type of system cannot be used ' +
                    'to calculate arbitrary surfaces (yet). It is recommended ' +
                    'to use string_vec != None.', stacklevel=2)
        # end RM_V2
            
        if string_vec is not None:
            def param_fct_proxy(t, k):
                return list(np.array(param_fct(t)) + k * np.array(string_vec))
            return Surface(self._m_handle, param_fct_proxy, **kwargs)

        return Surface(self._m_handle, param_fct, **kwargs)

    def line(self, param_fct, **kwargs):
        r"""TODO

        :param param_fct: Parametrizes the line with the parameter going from :math:`0` to :math:`1`.
        :type param_fct: function

        :param kwargs: Keyword arguments are passed to the :class:`Line`
            constructor. 

        :rtype: :class:`Line`

        .. note:: All directions / positions are given w.r.t. the
            inverse lattice vectors.
        """
        return Line(self._m_handle, param_fct, **kwargs)
