#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    05.02.2016 16:36:59 CET
# File:    _serializer_pickle.py


from ._serializer_core import serializer

import pickle

def pickle_setup(protocol=2):
    """
    Returns pickle as a serializer.

    
    :param protocol: The pickle protocol version that is used. The default is 2, which is the highest version that is compatible across all Python versions supported by Z2Pack.
    :type protocol: int
    """
    pickle.DEFAULT_PROTOCOL = protocol
    return pickle

serializer.register('pickle', pickle_setup)
