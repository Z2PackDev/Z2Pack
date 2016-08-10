#!/bin/bash
py.test -p no:cov-exclude --cov=z2pack --cov-report=html -Q -A
