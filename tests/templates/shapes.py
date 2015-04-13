#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    12.04.2015 20:27:58 CEST
# File:    shapes.py


from common import *

import numpy as np

class ShapesTestCase(CommonTestCase):
    def testsphere(self):
        sphere = z2pack.shapes.Sphere([1, 2, 3], 2)

        points = []
        for t in np.linspace(0, 1, 23):
            for k in np.linspace(0, 1, 27):
                points.append(sphere(t, k))
        self.assertContainerAlmostEqual(
            points, in_place_replace(points))

if __name__ == "__main__":
    unittest.main()
