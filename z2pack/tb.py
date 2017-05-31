#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains the class for creating systems based on `TBmodels <http://z2pack.ethz.ch/tbmodels>`_ tight-binding models.
"""

import copy
from collections import ChainMap

from fsc.export import export
from .hm import System as _HmSystem

@export
class System(_HmSystem):
    r"""
    System class for tight-binding models.

    :param tb_model: The tight-binding model.
    :type tb_model: Instance of :class:`tbmodels.Model` or one of its subclasses.

    :param kwargs:  Keyword arguments passed to :class:`.hm.System`.

    The ``pos`` and ``bands`` keywords of :class:`.hm.System` are determined from the ``tb_model`` unless otherwise specified.
    """
    def __init__(self, tb_model, **kwargs):
        super().__init__(
            hamilton=tb_model.hamilton,
            **ChainMap(kwargs, dict(
                pos=copy.deepcopy(tb_model.pos),
                bands=tb_model.occ
            ))
        )
