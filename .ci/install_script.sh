#!/bin/bash

# Author: Dominik Gresch <greschd@gmx.ch>

# Be verbose, and stop with error as soon there's one
set -ev

pip install codecov
pip install -U pip setuptools wheel

case "$INSTALL_TYPE" in
    dev)
        pip install -e .[dev]
        ;;
    dev_sdist)
        python setup.py sdist
        ls -1 dist/ | xargs -I % pip install dist/%[dev]
        ;;
    dev_bdist_wheel)
        python setup.py bdist_wheel
        ls -1 dist/ | xargs -I % pip install dist/%[dev]
        ;;
esac
