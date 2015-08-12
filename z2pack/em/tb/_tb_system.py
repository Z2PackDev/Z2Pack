#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.06.2015 11:02:53 CEST
# File:    _tb_system.py


from .. import System as _EmSystem
import copy

class System(_EmSystem):
    r"""
    System class for tight-binding models.

    :param tb_model: The tight-binding model.
    :type tb_model: Instance of :class:`z2pack.em.tb.Model` or one of its subclasses.

    :param kwargs:          are passed to the :class:`.Surface` constructor via
        :meth:`.surface`, which passes them to :meth:`wcc_calc<.Surface.wcc_calc>`, precedence:
        :meth:`wcc_calc<.Surface.wcc_calc>` > :meth:`.surface` > this (newer kwargs take precedence)
    """
    # RM_V2
    _new_style_system = True

    def __init__(self, tb_model, **kwargs):
        super(System, self).__init__(
            hamilton=tb_model.hamilton,
            pos=copy.deepcopy(tb_model.pos),
            occ=tb_model.occ,
            **kwargs
        )

