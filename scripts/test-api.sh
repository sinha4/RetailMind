#!/bin/sh
set -eu

if [ -x .venv/bin/python ]; then
  PYTHON=.venv/bin/python
else
  PYTHON=python
fi

MEMORY_BACKEND=seeded PYTHONPATH=apps/api/src "$PYTHON" -m pytest apps/api/tests \
  --cov=retailmind_api \
  --cov-report=term-missing \
  --cov-report=xml
