#!/usr/bin/env bash
# setup_dev_env.sh
# Bootstrap script for Unix-style environments that uses the normal Windows Python installation if mounted.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PYTHON_PATH="/c/Users/Student/AppData/Local/Python/bin/python.exe"
if [ ! -x "$PYTHON_PATH" ]; then
  echo "Python not found: $PYTHON_PATH"
  exit 1
fi

echo "Using Python: $PYTHON_PATH"
cd "$PROJECT_ROOT" || exit 1
"$PYTHON_PATH" -m venv .venv || exit 1
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r "$SCRIPT_DIR/requirements.txt"

if [ ! -f .env ] && [ -f "$SCRIPT_DIR/.env.example" ]; then
  cp "$SCRIPT_DIR/.env.example" .env
  echo ".env file created from .env.example. Please edit .env before running the app."
fi

echo "Bootstrap complete. Run 'python App/init_db.py' and then 'python App/app.py'."
