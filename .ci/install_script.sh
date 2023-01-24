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
        poetry install --only dev --no-root
        ls -1 dist/*.gz | xargs -I % pip install %[plot,tb]
        ;;
    dev_bdist_wheel)
        poetry build
        poetry install --only dev --no-root
        ls -1 dist/*.whl | xargs -I % pip install %[plot,tb]
        ;;
esac
