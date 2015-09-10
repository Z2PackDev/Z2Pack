#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.06.2015 12:03:43 CEST
# File:    _bases.py


import abc
import six
import inspect

class System(six.with_metaclass(abc.ABCMeta, object)):
    r"""
    Abstract base class for Z2Pack System classes.
    """
    __metaclass__ = abc.ABCMeta 

    @abc.abstractmethod
    def get_m(self, kpt):
        r"""
        Returns a list of overlap matrices :math:`M_{m,n}` corresponding to the given k-points.
        
        :param kpt: The list of k-points for which the overlap matrices are to be computed.
        :type kpt:  list
        """
        raise NotImplemented

class Surface(six.with_metaclass(abc.ABCMeta, object)):
    r"""
    Abstract base class for Z2Pack Surface classes. Note that surfaces can be defined as a function only, but they may have reduced functionality.
    """
    
    @abc.abstractmethod
    def __call__(self, s, t):
        r"""
        Returns the k-point at a given :math:`s, t \in [0, 1]^2`
        """
        raise NotImplemented

class Line(six.with_metaclass(abc.ABCMeta, object)):
    r"""
    Abstract base class for Z2Pack Line classes. Note that surfaces can be defined as a function only, but they may have reduced functionality.
    """
    
    @abc.abstractmethod
    def __call__(self, t):
        r"""
        Returns the k-point at a given :math:`s, t \in [0, 1]^2`
        """
        raise NotImplemented

