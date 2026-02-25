#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "memory" / ".state" / "auto_memory_sync_state.json"
INPUT_DIR = ROOT / "inputs" / "daily_logs"


def read_state() -> Dict[str, str]:
    if not STATE_FILE.exists():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def write_state(data: Dict[str, str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def latest_daily_signature() -> Dict[str, str]:
    files = sorted(INPUT_DIR.glob("*.md"))
    if not files:
        return {}
    latest = files[-1]
    stat = latest.stat()
    return {
        "path": str(latest),
        "mtime": str(int(stat.st_mtime)),
        "size": str(stat.st_size),
    }


def run_command(cmd: list[str]) -> int:
    process = subprocess.run(cmd, cwd=str(ROOT))
    return process.returncode


def main() -> None:
    state = read_state()
    sig = latest_daily_signature()
    daily_changed = (
        bool(sig)
        and (
            sig.get("path") != state.get("daily_path")
            or sig.get("mtime") != state.get("daily_mtime")
            or sig.get("size") != state.get("daily_size")
        )
    )

    if daily_changed:
        print("[RUN] 检测到 daily log 更新，执行 run_daily_ingest.sh", flush=True)
        ret = run_command(["bash", str(ROOT / "pipeline" / "run_daily_ingest.sh"), sig["path"]])
        if ret != 0:
            sys.exit(ret)
    else:
        print("[SKIP] daily log 无新增改动", flush=True)

    print("[RUN] 执行外部源增量提取（内部会自动判断是否跳过）", flush=True)
    ret = run_command(["bash", str(ROOT / "pipeline" / "run_external_ingest.sh"), "--days", "90"])
    if ret != 0:
        sys.exit(ret)

    next_state: Dict[str, str] = {
        "updated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if sig:
        next_state["daily_path"] = sig["path"]
        next_state["daily_mtime"] = sig["mtime"]
        next_state["daily_size"] = sig["size"]
    write_state(next_state)
    print(f"[OK] 状态已更新: {STATE_FILE}", flush=True)


if __name__ == "__main__":
    main()
