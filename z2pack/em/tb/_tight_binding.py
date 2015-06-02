#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    27.01.2015 12:10:02 CET
# File:    tight_binding.py


from ... import System as _Z2PackSystem

class System(_Z2PackSystem):
    r"""
    Subclass of :class:`z2pack.System` used for calculating system with a tight-
    binding model

    :param tb_hamilton:    Describes the system being calculated
    :type tb_hamilton:     :class:`z2pack.tb.Hamilton` object
    :param kwargs:          are passed to the :class:`.Surface` constructor via
        :meth:`.surface`, which passes them to :meth:`.wcc_calc`, precedence:
        :meth:`.wcc_calc` > :meth:`.surface` > this (newer kwargs take precedence)
    """
    # RM_V2
    _new_style_system = True
    
    def __init__(self,
                 tb_hamilton,
                 **kwargs):
        self._defaults = kwargs
        self._tb_hamilton = tb_hamilton

        self._m_handle = self._tb_hamilton._get_m

