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

class _AttributeCheck(six.with_metaclass(abc.ABCMeta, object)):
    r"""
    Base class for classes that need to check for the existence of some attributes after creating an instance.
    """
    def __init__(self, *args, **kwargs):
        """
        Check for the existence of a descriptor.
        """
        print(locals())
        print(globals())
        #~ required_attribs = ['descriptor']
        missing_attribs = []
        for attrib in self._required_attribs:
            if not hasattr(self, attrib):
                missing_attribs.append(attrib)
        if len(missing_attribs) > 0:
            raise TypeError('Surface cannot be instanitated without required attribute(s) ' + ' '.join(missing_attribs) + '.')

        super(_AttributeCheck, self).__init__(*args, **kwargs)

    @classmethod
    def __subclasshook__(cls, C):
        """
        Checks if C has all the required attributed that cls has.
        """
        for attrib in cls._required_attribs:
            if attrib not in C._required_attribs:
                return False

class Surface(_AttributeCheck):
    r"""
    Abstract base class for Z2Pack Surface classes. Note that surfaces can be defined as a function only, but they may have reduced functionality.
    """
    _required_attribs = ['descriptor']
    
    @abc.abstractmethod
    def __call__(self, s, t):
        r"""
        Returns the k-point at a given :math:`s, t \in [0, 1]^2`
        """
        raise NotImplemented

    @classmethod
    def __subclasshook__(cls, C):
        """
        Checks for the existence of a __call__ method.
        """
        if not '__call__' in [mem[0] for mem in inspect.getmembers(C, predicate=inspect.ismethod)]:
            return False
        return super(Surface, cls).__subclasshook__(C)
    
class Line(_AttributeCheck):
    r"""
    Abstract base class for Z2Pack Line classes. Note that surfaces can be defined as a function only, but they may have reduced functionality.
    """
    _required_attribs = ['descriptor']
    
    @abc.abstractmethod
    def __call__(self, t):
        r"""
        Returns the k-point at a given :math:`s, t \in [0, 1]^2`
        """
        raise NotImplemented

