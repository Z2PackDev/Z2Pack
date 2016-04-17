#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.06.2015 11:02:53 CEST
# File:    tb.py


from .em import System as _EmSystem
import copy

class System(_EmSystem):
    r"""
    System class for tight-binding models.

    :param tb_model: The tight-binding model.
    :type tb_model: Instance of :class:`tbmodels.Model` or one of its subclasses.
    """
    def __init__(self, tb_model, **kwargs):
        super(System, self).__init__(
            hamilton=tb_model.hamilton,
            pos=copy.deepcopy(tb_model.pos),
            bands=tb_model.occ,
        )
