#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.04.2016 10:21:56 CEST
# File:    _json_encoding.py

import json

from .surface import SurfaceResult

class SurfaceResultEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SurfaceResult):
            return dict(
                __surface_result__=True,
                data=obj.data,
                ctrl_convergence=obj.ctrl_convergence,
                ctrl_states=obj.ctrl_states
            )
        return super().default(self, obj)
