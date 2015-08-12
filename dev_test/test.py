#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.06.2015 08:51:02 CEST
# File:    test.py

import sys
sys.path.insert(0, '../')
from z2pack.em.tb._tb_model import _pos_to_idx, _idx_to_pos, _edge_detect_pos, _edge_detect_idx

print(_edge_detect_idx(13, [1, 3, 5]))
print(_edge_detect_pos([0, 2, 1], [1, 3, 5]))

