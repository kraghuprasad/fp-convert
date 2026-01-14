#!/usr/bin/env bash
set -euo pipefail  # abort on nonzero exitstatus, undefined var, or failed pipe
python -m pip uninstall -y fp-convert  # non-interactive, matches active interpreter
python -m build
python -m pip install --force-reinstall ./dist/*.whl
