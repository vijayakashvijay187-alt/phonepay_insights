#!/usr/bin/env bash
# First-time setup and dashboard. Safe to run again.
set -euo pipefail
cd "$(dirname "$0")"

echo "PhonePe Transaction Insights"
echo "This installs Python packages, starts the databases, loads PhonePe data, and opens the dashboard."

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed. Install Python 3.11 or newer, then run this script again."
  exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Install Docker Desktop or Docker Engine, start it, then run this script again."
  echo "https://docs.docker.com/get-docker/"
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but it is not running. Start Docker, then run this script again."
  exit 1
fi

if [[ ! -x .venv/bin/python ]]; then
  echo "Creating a Python environment in .venv"
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

bash scripts/setup.sh

echo ""
echo "Dashboard: http://localhost:8501"
echo "Stop the databases later with: bash scripts/teardown.sh"
exec .venv/bin/streamlit run app/streamlit_app.py --server.port 8501
