#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -d data/pulse/aggregated/transaction ]]; then
  echo "Pulse data already present in data/pulse"
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Git is not installed. Install Git, then run bash run.sh again."
  exit 1
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
git clone --depth 1 https://github.com/PhonePe/pulse.git "$tmpdir/pulse"
mkdir -p data/pulse
cp -a "$tmpdir/pulse/data/." data/pulse/
echo "Downloaded PhonePe Pulse into data/pulse"
