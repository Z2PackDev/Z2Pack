#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.06.2015 11:02:53 CEST
# File:    _tb_system.py


from .. import System as _EmSystem

class System(_EmSystem):
    r"""
    System class for tight-binding models
    
    :param tb_model: The tight-binding model.
    :type tb_model: Instance of :class:`z2pack.em.tb.Model` or one of its subclasses.
    """
    def __init__(self, tb_model, **kwargs):
        super(System, self).__init__(
            hamilton=tb_model.hamilton,
            pos=tb_model._pos,
            occ=tb_model._occ,
            **kwargs)

