#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "inputs" / "daily_logs"
MEMORY_DIR = ROOT / "memory"

AREA_FILES = {
    "topics": (
        MEMORY_DIR / "areas" / "topics" / "content-angles" / "items.json",
        MEMORY_DIR / "areas" / "topics" / "content-angles" / "summary.md",
        "Topics Summary",
    ),
    "formulas": (
        MEMORY_DIR / "areas" / "formulas" / "hook-patterns" / "items.json",
        MEMORY_DIR / "areas" / "formulas" / "hook-patterns" / "summary.md",
        "Hook Formula Summary",
    ),
    "wechat": (
        MEMORY_DIR / "areas" / "channels" / "wechat" / "items.json",
        MEMORY_DIR / "areas" / "channels" / "wechat" / "summary.md",
        "WeChat Channel Summary",
    ),
    "douyin": (
        MEMORY_DIR / "areas" / "channels" / "douyin" / "items.json",
        MEMORY_DIR / "areas" / "channels" / "douyin" / "summary.md",
        "Douyin Channel Summary",
    ),
}


def ensure_layout() -> None:
    (MEMORY_DIR / "daily").mkdir(parents=True, exist_ok=True)
    for items_path, summary_path, _ in AREA_FILES.values():
        items_path.parent.mkdir(parents=True, exist_ok=True)
        if not items_path.exists():
            items_path.write_text("[]\n", encoding="utf-8")
        if not summary_path.exists():
            summary_path.write_text("# Summary\n\n- 当前暂无结构化事实。\n", encoding="utf-8")


def latest_log_file() -> Path:
    files = sorted(INPUT_DIR.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"未找到日志文件: {INPUT_DIR}/*.md")
    return files[-1]


def parse_sections(text: str) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {}
    current = "__head__"
    sections[current] = []
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def norm_section_key(name: str) -> str:
    name = name.strip()
    mapping = {
        "元信息": "meta",
        "今日项目": "meta",
        "关键动作": "actions",
        "今日关键动作": "actions",
        "结果与证据": "evidence",
        "问题与决策": "decisions",
        "可提炼内容点（Topics）": "topics",
        "可提炼内容点": "topics",
        "可复用公式/结构（Formulas）": "formulas",
        "渠道观察": "channels",
        "今日结论（MEMORY候选）": "conclusions",
    }
    return mapping.get(name, name)


def parse_key_values(lines: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for line in lines:
        m = re.match(r"^\s*-\s*([^:：]+)[:：]\s*(.*)\s*$", line)
        if not m:
            continue
        key = m.group(1).strip()
        value = m.group(2).strip()
        out[key] = value
    return out


def parse_bullets(lines: List[str]) -> List[str]:
    out: List[str] = []
    for line in lines:
        m = re.match(r"^\s*-\s*(.+?)\s*$", line)
        if not m:
            continue
        value = m.group(1).strip()
        if not value:
            continue
        if re.match(r"^(结论|证据|置信度|项目名|阶段|今日目标|关键目标|问题|根因|决策|是否替代旧结论|若是，旧结论ID)[:：]", value):
            continue
        out.append(value)
    return out


def parse_conclusions(lines: List[str]) -> List[Dict[str, object]]:
    result: List[Dict[str, object]] = []
    current: Dict[str, object] | None = None
    for line in lines:
        s = line.strip()
        m_con = re.match(r"^-\s*结论[:：]\s*(.*)$", s)
        if m_con:
            if current and str(current.get("conclusion", "")).strip():
                result.append(current)
            current = {
                "conclusion": m_con.group(1).strip(),
                "evidence": "",
                "confidence": 0.75,
            }
            continue

        if current is None:
            continue

        m_evd = re.match(r"^-\s*证据[:：]\s*(.*)$", s)
        if m_evd:
            current["evidence"] = m_evd.group(1).strip()
            continue

        m_conf = re.match(r"^-\s*置信度.*[:：]\s*([0-9.]+)\s*$", s)
        if m_conf:
            try:
                current["confidence"] = float(m_conf.group(1))
            except ValueError:
                current["confidence"] = 0.75
            continue

    if current and str(current.get("conclusion", "")).strip():
        result.append(current)

    return result


def parse_date(log_file: Path, text: str) -> str:
    stem = log_file.stem
    if re.match(r"^\d{4}-\d{2}-\d{2}$", stem):
        return stem
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        return m.group(1)
    return dt.date.today().isoformat()


def make_id(prefix: str, date: str, fact: str) -> str:
    sig = hashlib.sha1(f"{prefix}|{date}|{fact}".encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{sig}"


def load_items(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return data
    return []


def save_items(path: Path, items: List[Dict[str, object]]) -> None:
    items_sorted = sorted(items, key=lambda x: (str(x.get("date", "")), str(x.get("id", ""))))
    path.write_text(json.dumps(items_sorted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def upsert_items(path: Path, new_items: List[Dict[str, object]]) -> Tuple[int, int]:
    existing = load_items(path)
    by_id = {str(item.get("id", "")): item for item in existing}
    inserted = 0
    updated = 0

    for item in new_items:
        item_id = str(item.get("id", ""))
        if not item_id:
            continue
        if item_id in by_id:
            by_id[item_id].update(item)
            updated += 1
        else:
            by_id[item_id] = item
            inserted += 1

    merged = list(by_id.values())
    save_items(path, merged)
    return inserted, updated


def write_summary(path: Path, title: str, items: List[Dict[str, object]]) -> None:
    active = [i for i in items if i.get("status", "active") == "active"]
    superseded = [i for i in items if i.get("status") == "superseded"]
    recent_active = sorted(active, key=lambda x: str(x.get("date", "")), reverse=True)[:8]

    lines = [
        f"# {title}",
        "",
        f"- 总事实数：{len(items)}",
        f"- Active：{len(active)}",
        f"- Superseded：{len(superseded)}",
        "",
        "## 最近 Active 事实",
    ]

    if not recent_active:
        lines.append("- 暂无")
    else:
        for item in recent_active:
            date = item.get("date", "")
            fact = item.get("fact", "")
            conf = item.get("confidence", "")
            lines.append(f"- [{date}] {fact} (置信度: {conf})")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def collect_area_items(date: str, source: str, evidence_lines: List[str], topics: List[str], formulas: Dict[str, str], channels: Dict[str, str]) -> Dict[str, List[Dict[str, object]]]:
    fallback_evidence = "；".join([x for x in evidence_lines if x]) or "来自 daily log"

    topic_items: List[Dict[str, object]] = []
    for t in topics:
        topic_items.append(
            {
                "id": make_id("topic", date, t),
                "date": date,
                "fact": t,
                "evidence": fallback_evidence,
                "source": source,
                "confidence": 0.80,
                "status": "active",
            }
        )

    formula_items: List[Dict[str, object]] = []
    for key, value in formulas.items():
        if not value:
            continue
        text = f"{key}：{value}"
        formula_items.append(
            {
                "id": make_id("formula", date, text),
                "date": date,
                "fact": text,
                "evidence": fallback_evidence,
                "source": source,
                "confidence": 0.78,
                "status": "active",
            }
        )

    wechat_items: List[Dict[str, object]] = []
    if channels.get("公众号"):
        fact = f"公众号渠道观察：{channels['公众号']}"
        wechat_items.append(
            {
                "id": make_id("wechat", date, fact),
                "date": date,
                "fact": fact,
                "evidence": fallback_evidence,
                "source": source,
                "confidence": 0.75,
                "status": "active",
            }
        )

    douyin_items: List[Dict[str, object]] = []
    if channels.get("抖音"):
        fact = f"抖音渠道观察：{channels['抖音']}"
        douyin_items.append(
            {
                "id": make_id("douyin", date, fact),
                "date": date,
                "fact": fact,
                "evidence": fallback_evidence,
                "source": source,
                "confidence": 0.75,
                "status": "active",
            }
        )

    return {
        "topics": topic_items,
        "formulas": formula_items,
        "wechat": wechat_items,
        "douyin": douyin_items,
    }


def write_daily_memory_file(
    date: str,
    source: str,
    meta: Dict[str, str],
    actions: List[str],
    evidence: Dict[str, str],
    decisions: Dict[str, str],
    topics: List[str],
    formulas: Dict[str, str],
    channels: Dict[str, str],
    conclusions: List[Dict[str, object]],
) -> Path:
    out_path = MEMORY_DIR / "daily" / f"{date}.md"
    lines: List[str] = [
        f"# {date} Memory Daily",
        "",
        f"- 来源：{source}",
        f"- 生成时间：{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Meta",
        f"- 项目名：{meta.get('项目名', '')}",
        f"- 阶段：{meta.get('阶段', '')}",
        f"- 目标：{meta.get('今日目标') or meta.get('关键目标') or ''}",
        "",
        "## Actions",
    ]

    if actions:
        lines.extend([f"- {x}" for x in actions])
    else:
        lines.append("- 暂无")

    lines.extend([
        "",
        "## Evidence",
    ])

    if evidence:
        for k, v in evidence.items():
            lines.append(f"- {k}：{v}")
    else:
        lines.append("- 暂无")

    lines.extend([
        "",
        "## Decisions",
    ])

    if decisions:
        for k, v in decisions.items():
            lines.append(f"- {k}：{v}")
    else:
        lines.append("- 暂无")

    lines.extend([
        "",
        "## Topics",
    ])
    lines.extend([f"- {x}" for x in topics] if topics else ["- 暂无"])

    lines.extend([
        "",
        "## Formulas",
    ])
    if formulas:
        for k, v in formulas.items():
            if v:
                lines.append(f"- {k}：{v}")
        if lines[-1] == "## Formulas":
            lines.append("- 暂无")
    else:
        lines.append("- 暂无")

    lines.extend([
        "",
        "## Channels",
    ])
    if channels:
        for k, v in channels.items():
            lines.append(f"- {k}：{v}")
    else:
        lines.append("- 暂无")

    lines.extend([
        "",
        "## Conclusions",
    ])

    if conclusions:
        for c in conclusions:
            lines.append(f"- 结论：{c.get('conclusion', '')}")
            lines.append(f"  - 证据：{c.get('evidence', '')}")
            lines.append(f"  - 置信度：{c.get('confidence', 0.75)}")
    else:
        lines.append("- 暂无")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def ensure_memory_md() -> Path:
    memory_md = MEMORY_DIR / "MEMORY.md"
    if memory_md.exists():
        return memory_md

    memory_md.write_text(
        """# Durable Memory (Layer 3)\n\n## Active Knowledge\n\n## Superseded Knowledge\n\n- 暂无\n\n## Last Updated\n\n- """
        + dt.date.today().isoformat()
        + "\n",
        encoding="utf-8",
    )
    return memory_md


def next_memory_index(text: str) -> int:
    nums = [int(m.group(1)) for m in re.finditer(r"^###\s+(\d+)\)", text, flags=re.M)]
    return max(nums) + 1 if nums else 1


def mark_superseded(memory_text: str, old_id: str, superseded_at: str, new_id: str) -> str:
    lines = memory_text.splitlines()
    in_target = False
    changed = False

    for i, line in enumerate(lines):
        if f"`{old_id}`" in line:
            in_target = True
            continue

        if in_target and line.startswith("### "):
            in_target = False

        if in_target and line.startswith("- 状态："):
            lines[i] = "- 状态：superseded"
            changed = True
            insert_lines = [
                f"- 被替代于：{superseded_at}",
                f"- 被替代为：`{new_id}`",
            ]
            pos = i + 1
            for extra in insert_lines:
                if extra not in lines[max(0, i - 6): i + 8]:
                    lines.insert(pos, extra)
                    pos += 1
            in_target = False

    return "\n".join(lines) + ("\n" if changed else "")


def append_memory_conclusions(memory_path: Path, date: str, source: str, conclusions: List[Dict[str, object]], decisions: Dict[str, str]) -> Tuple[int, List[str]]:
    if not conclusions:
        return 0, []

    text = memory_path.read_text(encoding="utf-8")
    existing_ids = set(re.findall(r"- ID:\s*`([^`]+)`", text))
    idx = next_memory_index(text)
    added = 0
    new_ids: List[str] = []

    blocks: List[str] = []
    for c in conclusions:
        conclusion = str(c.get("conclusion", "")).strip()
        if not conclusion:
            continue
        entry_id = f"mem-{hashlib.sha1(conclusion.encode('utf-8')).hexdigest()[:10]}"
        if entry_id in existing_ids:
            continue

        evidence = str(c.get("evidence", "") or "来自 daily log")
        confidence = c.get("confidence", 0.75)
        title = conclusion[:24] + ("..." if len(conclusion) > 24 else "")
        block = "\n".join(
            [
                f"### {idx}) {title}",
                f"- ID: `{entry_id}`",
                f"- 结论：{conclusion}",
                f"- 证据：{evidence}",
                f"- 来源：{source}",
                f"- 日期：{date}",
                f"- 置信度：{confidence}",
                "- 状态：active",
                "",
            ]
        )
        blocks.append(block)
        idx += 1
        added += 1
        existing_ids.add(entry_id)
        new_ids.append(entry_id)

    if blocks:
        anchor = "## Superseded Knowledge"
        if anchor in text:
            head, tail = text.split(anchor, 1)
            if not head.endswith("\n"):
                head += "\n"
            text = head + "\n" + "\n".join(blocks) + anchor + tail
        else:
            text = text.rstrip() + "\n\n" + "\n".join(blocks)

    should_supersede = decisions.get("是否替代旧结论（是/否）", "").strip() in {"是", "yes", "Yes", "Y", "y"}
    old_id = decisions.get("若是，旧结论ID", "").strip()
    if should_supersede and old_id and new_ids:
        text = mark_superseded(text, old_id, date, new_ids[0])

    text = re.sub(r"## Last Updated\n\n- .*", f"## Last Updated\n\n- {date}", text, flags=re.S)
    memory_path.write_text(text.rstrip() + "\n", encoding="utf-8")

    return added, new_ids


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest one daily log into 3-layer memory")
    parser.add_argument("--log", dest="log_path", default="", help="日志文件路径，默认自动选择最新")
    args = parser.parse_args()

    ensure_layout()

    log_file = Path(args.log_path).expanduser().resolve() if args.log_path else latest_log_file().resolve()
    if not log_file.exists():
        raise FileNotFoundError(f"日志文件不存在: {log_file}")

    text = log_file.read_text(encoding="utf-8")
    date = parse_date(log_file, text)
    sections_raw = parse_sections(text)

    sections: Dict[str, List[str]] = {}
    for key, lines in sections_raw.items():
        sections[norm_section_key(key)] = lines

    meta = parse_key_values(sections.get("meta", []))
    actions = parse_bullets(sections.get("actions", []))
    evidence = parse_key_values(sections.get("evidence", []))
    decisions = parse_key_values(sections.get("decisions", []))
    topics = parse_bullets(sections.get("topics", []))
    formulas = parse_key_values(sections.get("formulas", []))
    channels = parse_key_values(sections.get("channels", []))
    conclusions = parse_conclusions(sections.get("conclusions", []))

    source = str(log_file.relative_to(ROOT)) if str(log_file).startswith(str(ROOT)) else str(log_file)
    evidence_lines = [v for v in evidence.values() if v]

    area_new = collect_area_items(
        date=date,
        source=source,
        evidence_lines=evidence_lines,
        topics=topics,
        formulas=formulas,
        channels=channels,
    )

    counters: Dict[str, Tuple[int, int, int]] = {}
    for key, (items_path, summary_path, title) in AREA_FILES.items():
        inserted, updated = upsert_items(items_path, area_new.get(key, []))
        all_items = load_items(items_path)
        write_summary(summary_path, title, all_items)
        counters[key] = (inserted, updated, len(all_items))

    daily_path = write_daily_memory_file(
        date=date,
        source=source,
        meta=meta,
        actions=actions,
        evidence=evidence,
        decisions=decisions,
        topics=topics,
        formulas=formulas,
        channels=channels,
        conclusions=conclusions,
    )

    memory_md = ensure_memory_md()
    memory_added, memory_ids = append_memory_conclusions(memory_md, date, source, conclusions, decisions)

    print(f"[OK] Ingested log: {log_file}")
    print(f"[OK] Daily memory: {daily_path}")
    for key, (ins, upd, total) in counters.items():
        print(f"[OK] {key}: +{ins} inserted, {upd} updated, {total} total")
    print(f"[OK] Durable memory added: {memory_added}")
    if memory_ids:
        print("[OK] New memory IDs: " + ", ".join(memory_ids))


if __name__ == "__main__":
    main()
