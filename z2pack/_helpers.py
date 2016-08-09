#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.03.2016 10:21:06 CET
# File:    _helpers.py

"""Coding tools, not related to the 'physical/computation logic' of Z2Pack."""

import os
import tempfile
from collections import namedtuple, OrderedDict

import json
import pickle
import msgpack

from fsc.export import export

from . import _encoding

SerializerSpecs = namedtuple('SerializerSpecs', ['binary', 'encode_kwargs', 'decode_kwargs'])

SERIALIZER_SPECS = OrderedDict(
    [
        (msgpack, SerializerSpecs(
            binary=True,
            encode_kwargs=dict(default=_encoding.encode),
            decode_kwargs=dict(object_hook=_encoding.decode)
        )), 
        (json, SerializerSpecs(
            binary=False, 
            encode_kwargs=dict(default=_encoding.encode),
            decode_kwargs=dict(object_hook=_encoding.decode)
        )), 
        (pickle, SerializerSpecs(
            binary=True,
            encode_kwargs=dict(protocol=4), 
            decode_kwargs={}
        ))
    ]
)

EXT_MAPPING = {
    k.lower(): v for k, v in [
        ('p', pickle),
        ('pickle', pickle),
        ('msgpack', msgpack),
        ('json', json)
    ]
}

def _get_serializer(file_path):
    """Tries to determine the correct serializer from the file extension. If none can be determined, falls back to the default (msgpack)"""
    _, file_ext = os.path.splitext(file_path)
    try:
        return EXT_MAPPING[file_ext.lower()]
    except KeyError:
        return next(iter(SERIALIZER_SPECS.keys()))

@export
def save(obj, file_path, serializer='auto'):
    """Saves an object to the file given in ``file_path``. The saving is made atomic by first creating a temporary file and then moving to the ``file_path``.
    
    :param obj:         Object to be saved.
    
    :param file_path:   Path to the file.
    :type file_path:    str

    :param serializer:  The serializer to be used. Valid options are ``msgpack`` ``json`` and ``pickle``. By default, the serializer is determined from the file extension. If this does not work, ``msgpack`` is used. 
    :type serializer:   module
    """
    if serializer == 'auto':
        serializer = _get_serializer(file_path)
    specs = SERIALIZER_SPECS[serializer]
    with tempfile.NamedTemporaryFile(
        dir=os.path.dirname(os.path.abspath(file_path)),
        delete=False,
        mode='wb' if specs.binary else 'w'
    ) as f:
        serializer.dump(obj, f, **specs.encode_kwargs)
        os.replace(f.name, file_path)

@export
def load(file_path, serializer='auto'):
    """Loads the object that was saved to ``file_path``. 
    
    :param file_path:   Path to the file.
    :type file_path:    str
    
    :param serializer:  The serializer which should be used to load the result. By default, it tries to guess from the file extension, but all three serializers (JSON, msgpack, pickle) are tried if that does not succeed. If a specific serializer is given, the others are not tried.
    """
    if serializer == 'auto':
        serializer = _get_serializer(file_path)
        serializer_list = [serializer] + [
            k for k in SERIALIZER_SPECS.keys() if k is not serializer
        ]
    else:
        serializer_list = [serializer]
    for s in serializer_list:
        print(s)
        try:
            specs = SERIALIZER_SPECS[s]
            with open(file_path, 'rb' if specs.binary else 'r') as f:
                return s.load(f, **specs.decode_kwargs)
        except OSError as e:
            raise e
        except Exception as e:
            pass
    else:
        raise ValueError('File could not be deserialized with any of the used serializers ({}).'.format(', '.join([s.__name__ for s in serializer_list])))
            
