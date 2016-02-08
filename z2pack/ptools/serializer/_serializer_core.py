#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    05.02.2016 16:32:35 CET
# File:    _serializer_core.py

__all__ = ['serializer']

class SerializerHandle(object):
    """Proxy object which stores the backends, as well as the currently active backend."""    
    def __init__(self):
        self.active_backend = None
        self.backends = dict()

    def register(self, name, setup_fct):
        """Register a new backend. Must supply a setup function which returns the serializer object."""
        if name in self.backends.keys():
            raise ValueError('Serializer name exists already.')
        self.backends[name] = setup_fct

    def use(self, name='pickle', **kwargs):
        """Switch to a different backend. Keyword arguments for the setup function may be supplied."""
        try:
            new_backend = self.backends[name](**kwargs)
            if not (hasattr(new_backend, 'dump') and hasattr(new_backend, 'load')):
                raise TypeError('The serializer setup function did not produce a valid serializer.')
            self.active_backend = new_backend
        except KeyError:
            raise KeyError('No backend named \'{0}\''.format(name))

serializer = SerializerHandle()    
