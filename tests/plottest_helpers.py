#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    14.03.2016 13:10:14 CET
# File:    plottest_helpers.py

import tempfile

import os
import pytest
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.testing.compare import compare_images

@pytest.fixture()
def disable_diff_save(monkeypatch):
    def do_nothing(*args, **kwargs):
        pass
    monkeypatch.setattr(matplotlib.testing.compare, 'save_diff_image', do_nothing)
    
@pytest.fixture()
def assert_image_equal(disable_diff_save):
    def inner(name, tol=1e-6):
        path = './reference_plots/' + name + '.png'
        if not os.path.exists(path):
            plt.savefig(path)
            raise ValueError('Reference plot did not exist.')
        else:
            with tempfile.NamedTemporaryFile(suffix='.png') as fp:
                plt.savefig(fp.name)
                assert compare_images(path, fp.name, tol=tol, in_decorator=True) is None
    return inner
