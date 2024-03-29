#!/usr/bin/env python
"""
This module contains the class for creating systems based on `TBmodels <https://tbmodels.greschd.ch>`_ tight-binding models.
"""

from collections import ChainMap
import copy

from .hm import System as _HmSystem

__all__ = ["System"]


class System(_HmSystem):
    r"""
    System class for tight-binding models.

    :param tb_model: The tight-binding model.
    :type tb_model: Instance of :class:`tbmodels.Model` or one of its subclasses.

    :param kwargs:  Keyword arguments passed to :class:`.hm.System`.

    The ``pos``, ``bands`` and ``dim`` keywords of :class:`.hm.System` are determined from the ``tb_model`` unless otherwise specified.
    """

    def __init__(self, tb_model, **kwargs):
        super().__init__(
            hamilton=tb_model.hamilton,
            convention=2,
            **ChainMap(
                kwargs,
                dict(
                    pos=copy.deepcopy(tb_model.pos),
                    bands=tb_model.occ,
                    dim=tb_model.dim,
                ),
            ),
        )
