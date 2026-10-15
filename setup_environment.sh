#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
bash "$project_dir/framework/install_safal.sh" "$project_dir/.venv"
"$project_dir/.venv/bin/python" "$project_dir/train.py" --help
