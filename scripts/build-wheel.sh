#!/usr/bin/env bash
set -euo pipefail

# Build a wheel for the project into ./dist
rm -rf dist/
python -m pip install --upgrade pip setuptools wheel build
python -m build --wheel --outdir dist
echo "Wheel(s) written to ./dist"
