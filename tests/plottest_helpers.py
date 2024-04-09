"""
Helper fixtures for plot tests.
"""

# pylint: disable=unused-argument,redefined-outer-name

import os
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.testing.compare import compare_images
import pytest


@pytest.fixture()
def disable_diff_save(monkeypatch):
    """
    Do not save the diff of images if the test fails.
    """

    def do_nothing(*args, **kwargs):
        pass

    monkeypatch.setattr(matplotlib.testing.compare, "save_diff_image", do_nothing)


@pytest.fixture
def assert_image_equal(disable_diff_save, pytestconfig):
    """
    Save the current figure to a temporary file and check that it's the same as the reference image of the given name.
    """

    def inner(name, tol=1e-6):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "reference_plots", name + ".png"
        )

        if not os.path.exists(path):
            plt.savefig(path)
            raise ValueError("Reference plot did not exist.")

        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
            plt.savefig(temp_file.name)
            if not pytestconfig.option.no_plot_compare:
                assert compare_images(path, temp_file.name, tol=tol, in_decorator=True) is None

    return inner
