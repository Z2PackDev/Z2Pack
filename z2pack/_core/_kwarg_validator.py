#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.06.2015 11:48:12 CEST
# File:    _kwarg_validator.py

import re
import decorator

def _validate_kwargs(func=None, target=None):
    """
    checks if kwargs are in target's docstring
    if no target is given, target = func
    """
    @decorator.decorator
    def inner(func, *args, **kwargs):
        """decorated function"""
        if target is None:
            doc = func.__doc__
        else:
            doc = target.__doc__
        valid_kwargs = re.findall(':[\s]*param[\s]+([^:\s]+)', doc)
        for key in kwargs.keys():
            if key not in valid_kwargs:
                if target is None:
                    raise TypeError(func.__name__ +
                                    ' got an unexpected keyword ' +
                                    key)
                else:
                    raise TypeError(func.__name__ +
                                    ' got an unexpected keyword \'' +
                                    key + '\' for use in ' +
                                    target.__name__)
        return func(*args, **kwargs)

    if func is None:
        return inner
    else:
        return inner(func)
