#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    09.02.2016 10:08:45 CET
# File:    _convergence_abc.py

import abc
import six

@six.add_metaclass(abc.ABCMeta)
class ConvergenceTester(object):

    @abc.abstractmethod
    def update(self, data):
        pass

    @abc.abstractproperty
    def converged(self):
        pass
        
    @abc.abstractproperty
    def state(self):
        pass

class SurfaceConvergenceTester(ConvergenceTester):
    pass

class LineConvergenceTester(ConvergenceTester):
    pass
