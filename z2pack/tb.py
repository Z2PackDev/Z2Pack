#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.06.2015 11:02:53 CEST
# File:    tb.py

"""
This module contains the class for creating systems based on `TBmodels <http://z2pack.ethz.ch/tbmodels>`_ tight-binding models.
"""

import copy
from collections import ChainMap

from .em import System as _EmSystem

class System(_EmSystem):
    r"""
    System class for tight-binding models.

    :param tb_model: The tight-binding model.
    :type tb_model: Instance of :class:`tbmodels.Model` or one of its subclasses.
    
    :param kwargs:  Keyword arguments passed to :class:`.em.System`.

    The ``pos`` and ``bands`` keywords of :class:`.em.System` are determined from the ``tb_model`` unless otherwise specified.
    """
    def __init__(self, tb_model, **kwargs):
        super(System, self).__init__(
            hamilton=tb_model.hamilton,
            **ChainMap(kwargs, dict(
                pos=copy.deepcopy(tb_model.pos),
                bands=tb_model.occ
            ))
        )
