#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.06.2016 23:17:12 CEST
# File:    svg.py

import numpy as np
from addon.util import svg

LINE_PROPS = dict(stroke='#222222', stroke_width=30, fill='none')

STRETCH = np.sin(np.pi / 3)

pic = svg.canvas(width=300, height=200 * STRETCH)

pic.add(svg.rect(x=0, y=0, width=300, height=300, fill='#111111'))

pic.add(
    svg.path(
        d="""
        M0,0
        l {half_right},{down}
        l {right},0
        l {half_right},{up}
        l {right},0
        l {half_right},{down}
    """.format(
            half_right=50, right=100, down=100 * STRETCH, up=-100 * STRETCH
        ),
        **LINE_PROPS
    )
)
pic.add(
    svg.path(
        d="""
        M0,{bottom}
        l {half_right},{up}
        l {right},0
        l {half_right},{down}
        l {right},0
        l {half_right},{up}
    """.format(
            half_right=50,
            right=100,
            down=100 * STRETCH,
            up=-100 * STRETCH,
            bottom=200 * STRETCH
        ),
        **LINE_PROPS
    )
)

pic.write_svg('hex.svg')
