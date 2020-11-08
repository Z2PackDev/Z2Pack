#!/bin/bash
pytest -p no:cov-exclude --cov=z2pack --cov-report=html -Q -A
