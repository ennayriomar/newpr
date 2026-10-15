#!/usr/bin/env bash
# Portable CPU setup for SAFAL; historical runners retain their separate setup.
set -euo pipefail
safal_source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
safal_venv_dir="${1:-$safal_source_dir/.venv}"
if [ ! -x "$safal_venv_dir/bin/python" ]; then
  python3.12 -m venv "$safal_venv_dir"
fi
"$safal_venv_dir/bin/python" -c 'import sys; assert sys.version_info[:2] == (3,12), "SAFAL requires Python 3.12"'
"$safal_venv_dir/bin/python" -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.7.1+cpu torchvision==0.22.1+cpu
"$safal_venv_dir/bin/python" -m pip install -r "$safal_source_dir/requirements-safal.txt"
"$safal_venv_dir/bin/python" -m pip install --no-build-isolation --no-deps -e "$safal_source_dir"
"$safal_venv_dir/bin/python" -m safe_iad.safal_cli --help
