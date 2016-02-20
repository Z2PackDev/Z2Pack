#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    19.02.2016 16:30:58 MST
# File:    _control.py

from .._control_base import ConvergenceControl, IterationControl, SurfaceControl, StatefulControl
from .._utils import _get_max_move

class MaxMove(ConvergenceControl, SurfaceControl):
