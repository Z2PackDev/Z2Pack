#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    05.02.2016 16:36:59 CET
# File:    _serializer_pickle.py


from ._serializer_core import serializer

import pickle

def pickle_setup(protocol=pickle.HIGHEST_PROTOCOL):
    pickle.DEFAULT_PROTOCOL = protocol
    return pickle

serializer.register('pickle', pickle_setup)
