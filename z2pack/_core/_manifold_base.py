#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    18.02.2016 10:03:46 MST
# File:    _manifold_base.py

# The usefulness of these ABC is not clear...

@six.add_metaclass(abc.ABCMeta)
class Surface:
    r"""
    Abstract base class for Z2Pack Surface classes. Note that surfaces can be defined as a function only, but they may have reduced functionality.
    """
    
    @abc.abstractmethod
    def __call__(self, s, t):
        r"""
        Returns the k-point at a given :math:`s, t \in [0, 1]^2`
        """
        pass

@six.add_metaclass(abc.ABCMeta)
class Line:
    r"""
    Abstract base class for Z2Pack Line classes. Note that lines can be defined as a function only, but they may have reduced functionality.
    """
    
    @abc.abstractmethod
    def __call__(self, t):
        r"""
        Returns the k-point at a given :math:`s, t \in [0, 1]^2`
        """
        pass
