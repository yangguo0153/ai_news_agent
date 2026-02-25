#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT_DIR/pipeline/ingest_daily_log.py"

LOG_PATH="${1:-}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 未安装"
  exit 1
fi

if [ -n "$LOG_PATH" ]; then
  python3 "$SCRIPT" --log "$LOG_PATH"
else
  python3 "$SCRIPT"
fi
