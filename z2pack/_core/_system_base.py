#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.06.2015 12:03:43 CEST
# File:    _bases.py


import abc

class System(metaclass=abc.ABCMeta):
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
        pass
