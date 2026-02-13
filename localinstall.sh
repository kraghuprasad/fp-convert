#!/usr/bin/env bash
set -euo pipefail  # abort on nonzero exitstatus, undefined var, or failed pipe
source .venv/bin/activate
python -m pip uninstall -y fp-convert || true  # ignore if not installed
rm -rf ./dist  # clean old build artifacts
python -m build
python -m pip install --force-reinstall ./dist/*.whl
