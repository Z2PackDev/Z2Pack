#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    14.02.2015 00:14:16 CET
# File:    logger.py

from __future__ import print_function

from .string_tools import cbox

"""
A simple logging tool which can keep track of an arbitrary number of
``events``. Each event is described by a tuple containing its name and
a format string.
"""


class Logger:
    def __init__(self, *events):
        self._events = {}
        for event in events:
            self._events[event.name()] = event
        #~ self._events = {event.name(): event for event in events}

    def __str__(self):
        output = ''
        for name, event in self._events.items():
            output += str(event) + '\n\n'
        return output.rstrip()

    def log(self, name, *msg):
        self._events[name].log(*msg)

    def reset(self):
        for name, event in self._events.items():
            event.reset()

class Event:
    """
    Basic event class
    """
    def __init__(self, name, format_string, zero_string = None):
        self._name = name
        self._format_string = format_string
        self._occurences = []
        self._zero_string = zero_string

    def log(self, *msg):
        self._occurences.append(msg)
        
    def name(self):
        return self._name

    def __str__(self):
        if len(self._occurences) == 0:
            if self._zero_string is not None:
                return self._zero_string
            else:
                return 'No {0} occurences'.format(self._name)
        else:
            output = self._name.upper() + '\n'
            for occ in self._occurences:
                output += self._format_string.format(*occ)
                output += '\n'
            return output.rstrip()

    def reset(self):
        self._occurences = []

class ConvFail(Event):
    """
    Convergence failures
    """
    def __str__(self):
        if len(self._occurences) == 0:
            if self._zero_string is not None:
                return self._zero_string
            else:
                return '{0} never failed'.format(self._name.upper())
        else:
            output = self._name.upper() + ' failed in the following instances:\n'
            for occ in self._occurences:
                output += self._format_string.format(*occ)
                output += '\n'
            return output.rstrip()
    
    
