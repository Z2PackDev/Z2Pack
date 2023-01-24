#!/bin/bash

# Author: Dominik Gresch <greschd@gmx.ch>

# Be verbose, and stop with error as soon there's one
set -ev

pip install codecov
pip install -U pip setuptools wheel poetry
poetry config virtualenvs.create false

case "$INSTALL_TYPE" in
    dev)
        poetry install -E tb -E plot
        ;;
    dev_sdist)
        poetry build
        pip install dist/*.gz
        poetry install --only dev
        ;;
    dev_bdist_wheel)
        poetry build
        pip install dist/*.whl
        poetry install --only dev
        ;;
esac
