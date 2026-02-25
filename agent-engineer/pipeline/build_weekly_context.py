#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
MEMORY_DIR = ROOT / "memory"
OUTPUT_WEEKLY = ROOT / "outputs" / "weekly"


def collect_daily_files(days: int) -> List[Path]:
    daily_dir = MEMORY_DIR / "daily"
    files = sorted(daily_dir.glob("*.md"))
    if not files:
        return []
    return files[-days:]


def parse_active_memory(memory_md: Path, limit: int = 8) -> List[Dict[str, str]]:
    if not memory_md.exists():
        return []

    text = memory_md.read_text(encoding="utf-8")
    blocks = re.findall(r"(?ms)^###\s+\d+\).*?(?=^###\s+\d+\)|^##\s+Superseded|\Z)", text)
    out: List[Dict[str, str]] = []

    for block in blocks:
        if "- 状态：active" not in block:
            continue
        id_m = re.search(r"- ID:\s*`([^`]+)`", block)
        c_m = re.search(r"- 结论：(.+)", block)
        e_m = re.search(r"- 证据：(.+)", block)
        d_m = re.search(r"- 日期：(.+)", block)
        conclusion = c_m.group(1).strip() if c_m else ""
        entry_id = id_m.group(1).strip() if id_m else ""
        if not entry_id and conclusion:
            entry_id = "legacy-" + hashlib.sha1(conclusion.encode("utf-8")).hexdigest()[:10]
        out.append(
            {
                "id": entry_id,
                "conclusion": conclusion,
                "evidence": e_m.group(1).strip() if e_m else "",
                "date": d_m.group(1).strip() if d_m else "",
            }
        )

    out = [x for x in out if x.get("conclusion")]
    out.sort(key=lambda x: x.get("date", ""), reverse=True)
    return out[:limit]


def collect_summary_files() -> List[Path]:
    summary_files = sorted((MEMORY_DIR / "areas").glob("**/summary.md"))
    return [path for path in summary_files if path.exists()]


def read_summary_blocks() -> List[str]:
    blocks: List[str] = []
    for p in collect_summary_files():
        if not p.exists():
            continue
        content = p.read_text(encoding="utf-8").strip()
        rel = p.relative_to(ROOT)
        blocks.append(f"### {rel}\n\n{content}")
    return blocks


def build_weekly_pack(days: int, daily_files: List[Path], active_memory: List[Dict[str, str]], summaries: List[str], week_tag: str, out_file: Path) -> None:
    lines: List[str] = [
        f"# Weekly Input Pack ({week_tag})",
        "",
        f"- 生成时间：{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- 聚合天数：{days}",
        f"- 日志数量：{len(daily_files)}",
        "",
        "## Layer 3: Durable Memory (Active)",
    ]

    if not active_memory:
        lines.append("- 暂无 active 结论")
    else:
        for item in active_memory:
            lines.append(f"- [{item['date']}] {item['conclusion']} (ID: {item['id']})")
            lines.append(f"  - 证据：{item['evidence']}")

    lines.extend([
        "",
        "## Layer 1: Knowledge Graph Summaries",
    ])

    if not summaries:
        lines.append("- 暂无 summary")
    else:
        for block in summaries:
            lines.extend([block, ""])

    lines.extend([
        "## Layer 2: Daily Timeline",
    ])

    if not daily_files:
        lines.append("- 暂无 daily 记录")
    else:
        for f in daily_files:
            rel = f.relative_to(ROOT)
            lines.extend([
                "",
                f"---\n\n### Source: {rel}",
                "",
                f.read_text(encoding="utf-8").strip(),
            ])

    out_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_publish_plan(week_tag: str, active_memory: List[Dict[str, str]], daily_files: List[Path], out_file: Path) -> None:
    evidence_sources = [str(f.relative_to(ROOT)) for f in daily_files]
    lines = [
        f"# Publish Plan ({week_tag})",
        "",
        "## 先看这些证据源",
    ]

    if evidence_sources:
        lines.extend([f"- {x}" for x in evidence_sources])
    else:
        lines.append("- 暂无")

    lines.extend([
        "",
        "## 本周建议优先级",
        "1. A: 公众号深度文（建立信任）",
        "2. B: 抖音口播（扩大触达）",
        "3. C: 二次分发短内容（扩大复用）",
        "",
        "## 可用核心结论（来自 MEMORY）",
    ])

    if active_memory:
        for item in active_memory[:5]:
            lines.append(f"- {item['conclusion']}（ID: {item['id']}）")
    else:
        lines.append("- 暂无")

    lines.extend([
        "",
        "## Content A（公众号深度文）",
        "- 标题：",
        "- 核心观点：",
        "- 证据引用：",
        "- CTA：",
        "",
        "## Content B（抖音口播）",
        "- 钩子：",
        "- 主线：",
        "- 证据引用：",
        "- CTA：",
        "",
        "## Content C（二次分发）",
        "- 渠道：",
        "- 开场：",
        "- 证据引用：",
        "- CTA：",
    ])

    out_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build weekly context pack from memory layers")
    parser.add_argument("--days", type=int, default=7, help="聚合最近 N 天")
    args = parser.parse_args()

    days = max(1, args.days)
    week_tag = dt.datetime.now().strftime("%G-W%V")
    out_dir = OUTPUT_WEEKLY / week_tag
    out_dir.mkdir(parents=True, exist_ok=True)

    pack_file = out_dir / "weekly_input_pack.md"
    plan_file = out_dir / "publish_plan.md"

    daily_files = collect_daily_files(days)
    active_memory = parse_active_memory(MEMORY_DIR / "MEMORY.md", limit=8)
    summaries = read_summary_blocks()

    build_weekly_pack(days, daily_files, active_memory, summaries, week_tag, pack_file)
    build_publish_plan(week_tag, active_memory, daily_files, plan_file)

    print(f"[OK] Weekly pack: {pack_file}")
    print(f"[OK] Publish plan: {plan_file}")
    print(f"[OK] Daily files used: {len(daily_files)}")
    print(f"[OK] Active memory used: {len(active_memory)}")


if __name__ == "__main__":
    main()
