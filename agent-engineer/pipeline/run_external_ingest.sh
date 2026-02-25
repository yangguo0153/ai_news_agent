#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT_DIR/pipeline/ingest_external_atomic.py"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 未安装"
  exit 1
fi

python3 "$SCRIPT" "$@"
