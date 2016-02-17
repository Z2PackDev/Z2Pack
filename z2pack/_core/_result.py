#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.02.2016 15:02:23 CET
# File:    _result.py

from ptools.locker import Locker

import six


@six.add_metaclass(Locker)
class Result(object):
    def __init__(self, data, ctrl_states):
        self.data = data
        self.ctrl_states = ctrl_states
