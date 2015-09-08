#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.09.2015 11:07:35 CEST
# File:    _run_surface.py

from __future__ import division, print_function

from ._utils import _convcheck
from ..ptools import string_tools
from ._result import SurfaceResult

import sys
import time
import copy
import itertools
import numpy as np
import scipy.linalg as la

def run_surface(
    system,
    surface,
    pos_tol=1e-2,
    gap_tol=2e-2,
    move_tol=0.3,
    iterator=range(8, 27, 2),
    min_neighbour_dist=0.01,
    num_strings=11,
    verbose=True,
    result=None,
    pfile=None,
    werr=True,
):
    r"""
    TODO
    """
    return _RunSurfaceImpl(**locals()).run()

class _RunSurfaceImpl(object):
    def __init__(self, system, surface, **kwargs):
        # automatically parse kwargs except ignore_kwargs into self
        ignore_kwargs = ['result']
        for key, val in kwargs.items():
            if key not in ignore_kwargs:
                setattr(self, key, val)

        # ---- SYSTEM AND SURFACE ----
        self.get_m = lambda N: system.get_m(self._get_kpt(N))
        self.surface = surface
        
        # ---- NORMALIZE ITERATOR ----
        if isinstance(self.iterator, int):
            self.iterator = iter([self.iterator])
        if not hasattr(self.iterator, '__next__'): # replace by abc.Iterator
            self.iterator = iter(self.iterator)
        if self.pos_tol is None:
            # iterator shouldn't be deleted (used for first step also)
            # instead, it is modified to reflect pos_tol=None
            self.iterator = [next(self.iterator)]
            
        # ---- CREATE DESCRIPTOR ----
        self.descriptor = dict()
        described_objects = [['system', system], ['surface', surface]]
        for name, obj in described_objects:
            try:
                self.descriptor[name] = obj.descriptor
            except AttributeError:
                self.descriptor[name] = None

        # ---- CREATE SurfaceResult ----
        if kwargs['result'] is None:
            self.result = SurfaceResult(self.descriptor['surface'])
        else:
            if not isinstance(result, SurfaceResult):
                raise TypeError('Invalid type of surface result: {0}, must be SurfaceResult'.format(type(result)))
            if self.descriptor != kwargs['result'].descriptor:
                msg = 'Current surface descriptor {0} does not match pre-existing descriptor {1}'.format(self.descriptor, kwargs['result'].descriptor)
                if werr:
                    raise ValueError(msg)
                else:
                    warnings.warn(msg)
            self.result = kwargs['result']

        # ---- CREATE PRINT_VARS ----
        if self.verbose:
            self.print_vars = {key: self.__dict__[key] for key in [
                'pos_tol',
                'gap_tol',
                'move_tol',
                'move_tol',
                'min_neighbour_dist',
                'num_strings',
                'verbose',
                'werr',
                'pfile',
            ]}
            iterator, self.iterator = itertools.tee(self.iterator, 2)
            self.print_vars['iterator'] = list(iterator)
        print(self.__dict__)

    def run(self):
        pass
    
