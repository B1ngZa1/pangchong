#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_executable="${PYTHON_BIN:-python}"

cd "$repository_root"
"$python_executable" scripts/check_structure.py

cd "$repository_root/ecommerce/frontend"
npm run check

cd "$repository_root/ecommerce/backend"
"$python_executable" -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11 or newer is required'; import pytest, alembic"
"$python_executable" -m compileall -q app
"$python_executable" -m pytest
"$python_executable" -m alembic heads
