#!/usr/bin/env python

# Copyright © 2020 Elijah Shaw-Rutschman

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Interpolates aliases in YAML.
"""

import pathlib

from ruamel import yaml


class InterpolatingDumper(yaml.RoundTripDumper):
    def ignore_aliases(self, data):
        # Always interpolate aliases
        return True


def interpolate_aliases(in_stream, out_stream):
    data = yaml.load(in_stream, Loader=yaml.RoundTripLoader)
    if "_anchors" in data:
        # Remove top-level _anchors section
        del data["_anchors"]
    out_stream.write(yaml.dump(data, Dumper=InterpolatingDumper))


if __name__ == "__main__":
    ROOT_DIR = pathlib.Path(__file__).absolute().parent.parent
    GITHUB_DIR = ROOT_DIR / ".github"

    TEMPLATE_DIR = GITHUB_DIR / "workflows_source"
    assert TEMPLATE_DIR.exists()

    WORKFLOW_DIR = GITHUB_DIR / "workflows"
    assert WORKFLOW_DIR.exists()

    for in_file in TEMPLATE_DIR.iterdir():
        out_file = WORKFLOW_DIR / in_file.name
        with open(in_file) as in_f, open(out_file, "w") as out_f:
            interpolate_aliases(in_f, out_f)
