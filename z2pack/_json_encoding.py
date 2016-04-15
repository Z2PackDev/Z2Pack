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

#~ class LineDataEncoder(EigenstateLineDataEncoder, OverlapLineDataEncoder):
    #~ def default(self, obj):
        #~ return super().default(obj)


@export
class LineResultEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, LineResult):
            return dict(
                __line_result__=True,
                data=EigenstateLineDataEncoder.default(self, obj.data),
                ctrl_convergence=obj.ctrl_convergence,
                ctrl_states=obj.ctrl_states
            )
        return super().default(obj)

print(LineResultEncoder.__mro__)

class SurfaceLineEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SurfaceLine):
            return dict(
                __surface_line__=True,
                t=obj.t,
                result=LineResultEncoder.default(self, obj.result)
            )
        return super().default(obj)

class SurfaceDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SurfaceData):
            return dict(
                __surface_data__=True,
                lines=[SurfaceLineEncoder.default(self, line) for line in obj.lines]
            )
        return super().default(obj)

@export
class SurfaceResultEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SurfaceResult):
            return dict(
                __surface_result__=True,
                data=SurfaceDataEncoder.default(self, obj.data),
                #~ ctrl_convergence=obj.ctrl_convergence,
                #~ ctrl_states=obj.ctrl_states
            )
        return super().default(obj)
