#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.04.2016 10:21:56 CEST
# File:    _json_encoding.py

import json

from fsc.export import export

from .surface._result import SurfaceResult
from .surface._data import SurfaceData, SurfaceLine
from .line import LineResult, OverlapLineData, EigenstateLineData

class EigenstateLineDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, EigenstateLineData):
            return dict(
                __eigenstate_line_data__=True,
                eigenstates=obj.eigenstates
            )
        return super().default(obj)

class OverlapLineDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, OverlapLineData):
            return dict(
                __overlap_line_data__=True,
                overlaps=obj.overlaps
            )
        return super().default(obj)

@export
class LineResultEncoder(OverlapLineDataEncoder, EigenstateLineDataEncoder):
    def default(self, obj):
        if isinstance(obj, LineResult):
            return dict(
                __line_result__=True,
                data=obj.data,
                ctrl_convergence=obj.ctrl_convergence,
                ctrl_states=obj.ctrl_states
            )
        return super().default(obj)

print(LineResultEncoder.__mro__)

class SurfaceLineEncoder(LineResultEncoder):
    def default(self, obj):
        if isinstance(obj, SurfaceLine):
            return dict(
                __surface_line__=True,
                t=obj.t,
                result=obj.result
            )
        return super().default(obj)

class SurfaceDataEncoder(SurfaceLineEncoder):
    def default(self, obj):
        if isinstance(obj, SurfaceData):
            return dict(
                __surface_data__=True,
                lines=list(obj.lines)
            )
        return super().default(obj)

@export
class SurfaceResultEncoder(SurfaceDataEncoder):
    def default(self, obj):
        if isinstance(obj, SurfaceResult):
            return dict(
                __surface_result__=True,
                data=super().encode(obj.data),
                #~ ctrl_convergence=obj.ctrl_convergence,
                #~ ctrl_states=obj.ctrl_states
            )
        return super().default(obj)
