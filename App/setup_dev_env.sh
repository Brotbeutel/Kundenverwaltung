#!/usr/bin/env bash
# setup_dev_env.sh
# Bootstrap script for Unix-style environments that uses the normal Windows Python installation if mounted.

PYTHON_PATH="/c/Users/Student/AppData/Local/Python/bin/python.exe"
if [ ! -x "$PYTHON_PATH" ]; then
  echo "Python not found: $PYTHON_PATH"
  exit 1
fi

echo "Using Python: $PYTHON_PATH"
"$PYTHON_PATH" -m venv .venv || exit 1
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo ".env file created from .env.example. Please edit .env before running the app."
fi

echo "Bootstrap complete. Run 'python init_db.py' and then 'python app.py'."
