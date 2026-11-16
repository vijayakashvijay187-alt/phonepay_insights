#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "${1:-}" == "--reset" ]]; then
  docker compose down -v
fi

if [[ -x .venv/bin/python ]]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

bash scripts/download_data.sh
docker compose up -d
"$PYTHON" scripts/setup.py
"$PYTHON" scripts/build_report.py
echo "PhonePe warehouse is ready. Dashboard: streamlit run app/streamlit_app.py"
