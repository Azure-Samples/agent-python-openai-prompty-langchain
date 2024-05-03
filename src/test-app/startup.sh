#!/bin/bash

# Print commands and their arguments as they are executed
set -x
ls

pip install poetry==1.6.1
poetry config virtualenvs.create false
pip install uvicorn

python --version
# Install any dependencies (if not already installed)
poetry install --no-interaction --no-ansi

# Start the Uvicorn server
exec uvicorn app.server:app --host 0.0.0.0 --port 5001
