#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
MEMORY_DIR = ROOT / "memory"
AREA_DIR = MEMORY_DIR / "areas" / "profile" / "subject-object-actions"
ITEMS_FILE = AREA_DIR / "items.json"
SUMMARY_FILE = AREA_DIR / "summary.md"
STATE_FILE = MEMORY_DIR / ".state" / "external_ingest_state.json"

SOURCE_1 = Path("/Users/will/Desktop/通往AGI之路")
SOURCE_2 = Path("/Users/will/Library/Mobile Documents/iCloud~md~obsidian/Documents/我有一个想法1.1/99_Daily")

SOURCE_EXTS = {".md", ".markdown", ".txt"}
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".idea",
    ".vscode",
}

SOURCE1_EXACT_NAMES = {
    "progress.md",
    "task_plan.md",
    "findings.md",
    "memory.md",
    "index.md",
    "profile.md",
}

SOURCE1_NAME_KEYWORDS = (
    "日志",
    "log",
    "daily",
    "summary",
    "复盘",
    "progress",
    "task_plan",
    "findings",
    "memory",
    "思考",
)

CORE_TAG_KEYWORDS: Sequence[Tuple[str, Sequence[str], int]] = [
    (
        "洞察",
        (
            "我发现",
            "我认为",
            "我理解",
            "结论",
            "本质",
            "核心",
            "关键",
            "不是",
            "而是",
            "原则",
            "方法",
            "意味着",
        ),
        2,
    ),
    (
        "里程碑",
        (
            "完成",
            "落地",
            "上线",
            "发布",
            "交付",
            "跑通",
            "验证通过",
            "产出",
            "搭建",
            "实现",
            "闭环",
            "自动化",
        ),
        2,
    ),
    (
        "失败复盘",
        (
            "失败",
            "报错",
            "踩坑",
            "问题",
            "根因",
            "没成功",
            "崩溃",
            "抽风",
            "焦虑",
            "卡住",
            "风险",
            "误判",
        ),
        2,
    ),
    (
        "奇思妙想",
        (
            "想法",
            "设想",
            "灵感",
            "如果",
            "也许",
            "可以",
            "希望",
            "尝试",
            "进化",
            "机制",
            "策略",
            "未来",
        ),
        2,
    ),
]

AUX_TAG_KEYWORDS: Sequence[Tuple[str, Sequence[str], int]] = [
    ("偏好", ("喜欢", "不喜欢", "讨厌", "看不起", "爽", "热爱"), 1),
    ("实践", ("实操", "运行", "实现", "做了", "搭建", "改造", "验证"), 1),
]


def ensure_layout() -> None:
    AREA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not ITEMS_FILE.exists():
        ITEMS_FILE.write_text("[]\n", encoding="utf-8")
    if not SUMMARY_FILE.exists():
        SUMMARY_FILE.write_text("# High-Value Capsules Summary\n\n- 暂无高价值原子信息。\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest high-value external notes as compact capsules")
    parser.add_argument("--days", type=int, default=90, help="仅处理最近 N 天（按文件修改时间）")
    parser.add_argument("--max-per-file", type=int, default=2, help="每个文件最多提取条数")
    parser.add_argument("--max-total", type=int, default=60, help="最终最多保留条数")
    parser.add_argument("--force", action="store_true", help="忽略状态缓存，强制执行")
    return parser.parse_args()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def path_has_allowed_keyword(path: Path) -> bool:
    name = path.name.lower()
    if name in SOURCE1_EXACT_NAMES:
        return True
    if any(keyword in name for keyword in SOURCE1_NAME_KEYWORDS):
        return True

    path_lower = "/".join(part.lower() for part in path.parts)
    if "/.agent/memory/" in path_lower:
        return True
    if "/memory/" in path_lower and name.endswith(".md"):
        return True
    return False


def list_candidate_files(days: int) -> List[Path]:
    cutoff_ts = (dt.datetime.now() - dt.timedelta(days=max(days, 1))).timestamp()
    out: List[Path] = []

    if SOURCE_1.exists():
        for current, dirs, files in os.walk(SOURCE_1):
            current_path = Path(current)
            if is_within(current_path, ROOT):
                dirs[:] = []
                continue
            dirs[:] = sorted([d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".venv")])
            files = sorted(files)

            for filename in files:
                file_path = current_path / filename
                if file_path.suffix.lower() not in SOURCE_EXTS:
                    continue
                if not path_has_allowed_keyword(file_path):
                    continue
                try:
                    stat = file_path.stat()
                except OSError:
                    continue
                if stat.st_mtime < cutoff_ts:
                    continue
                out.append(file_path)

    if SOURCE_2.exists():
        for file_path in sorted(SOURCE_2.glob("*.md")):
            try:
                stat = file_path.stat()
            except OSError:
                continue
            if stat.st_mtime < cutoff_ts:
                continue
            out.append(file_path)

    unique = sorted(set(out), key=lambda p: (-_mtime(p), str(p)))
    return unique


def _mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def fingerprint(paths: Sequence[Path], days: int, max_per_file: int, max_total: int) -> str:
    parts = [
        "schema=v2-compact",
        f"days={days}",
        f"max_per_file={max_per_file}",
        f"max_total={max_total}",
    ]
    for path in paths:
        try:
            st = path.stat()
        except OSError:
            continue
        parts.append(f"{path}|{int(st.st_mtime)}|{st.st_size}")
    return hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()


def read_state() -> Dict[str, object]:
    if not STATE_FILE.exists():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def write_state(content: Dict[str, object]) -> None:
    STATE_FILE.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_text(raw: str) -> str:
    text = raw.replace("\r", "\n")
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"!\[\[[^\]]+\]\]", " ", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*]\s*", "", text, flags=re.M)
    return text


def split_sentences(text: str) -> List[str]:
    chunks = re.split(r"[。！？!?；;\n]+", text)
    out: List[str] = []
    for chunk in chunks:
        sentence = re.sub(r"\s+", " ", chunk).strip()
        if len(sentence) < 12 or len(sentence) > 220:
            continue
        if sentence.startswith(("-", "*", "|")):
            sentence = sentence.lstrip("-*| ").strip()
        if sentence:
            out.append(sentence)
    return out


def is_low_signal(sentence: str) -> bool:
    if sentence.count("|") >= 2:
        return True
    if re.search(r"第\d+[-~]\d+行", sentence):
        return True
    if re.search(r"\[[ xX]\]", sentence):
        return True
    if sentence.startswith(("Phase ", "Session ", "Status:", "状态：")):
        return True
    if re.search(r"[A-Za-z]:\\|/Users/|\.py|\.md", sentence):
        return True
    return False


def normalize_fact(sentence: str) -> str:
    fact = sentence.strip()
    fact = re.sub(r"^(结论|洞察|问题|根因|决策|想法|复盘|经验|教训|核心)[:：]\s*", "", fact)
    fact = re.sub(r"^(我发现|我认为|我理解|其实|本质上|所以|因此)\s*", "", fact)
    fact = re.sub(r"\s+", " ", fact).strip(" ，,。；;")
    if len(fact) > 80:
        fact = fact[:80].rstrip() + "..."
    return fact


def compact_key(text: str) -> str:
    compact = re.sub(r"[\W_]+", "", text.lower())
    return compact[:120]


def score_sentence(sentence: str) -> Tuple[int, List[str]]:
    score = 0
    tags: Set[str] = set()

    lowered = sentence.lower()
    for tag, keywords, weight in CORE_TAG_KEYWORDS:
        if any(keyword.lower() in lowered for keyword in keywords):
            tags.add(tag)
            score += weight

    for tag, keywords, weight in AUX_TAG_KEYWORDS:
        if any(keyword.lower() in lowered for keyword in keywords):
            tags.add(tag)
            score += weight

    if re.search(r"\d", sentence):
        score += 1
    if re.search(r"(分钟|小时|天|周|月|年|%|次)", sentence):
        score += 1
    if 20 <= len(sentence) <= 120:
        score += 1

    if not any(tag in tags for tag in ("洞察", "里程碑", "失败复盘", "奇思妙想")):
        return 0, []

    return score, sorted(tags)


def parse_date(path: Path) -> str:
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    if date_match:
        return date_match.group(1)
    try:
        ts = path.stat().st_mtime
    except OSError:
        return dt.date.today().isoformat()
    return dt.date.fromtimestamp(ts).isoformat()


def parse_file(path: Path, max_per_file: int) -> List[Dict[str, object]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="utf-8", errors="ignore")

    cleaned = clean_text(raw)
    sentences = split_sentences(cleaned)
    date = parse_date(path)
    source = str(path)

    candidates: List[Dict[str, object]] = []
    seen: Set[str] = set()
    for sentence in sentences:
        if is_low_signal(sentence):
            continue
        score, tags = score_sentence(sentence)
        if score < 5:
            continue

        fact = normalize_fact(sentence)
        if len(fact) < 12:
            continue
        if set(tags) == {"里程碑"} and len(fact) < 20:
            continue
        key = compact_key(fact)
        if not key or key in seen:
            continue
        seen.add(key)

        candidates.append(
            {
                "date": date,
                "fact": fact,
                "source": source,
                "tags": tags,
                "_score": score,
            }
        )

    candidates.sort(key=lambda x: (int(x.get("_score", 0)), -len(str(x.get("fact", "")))), reverse=True)
    return candidates[: max(1, max_per_file)]


def select_compact_capsules(parsed: Iterable[Dict[str, object]], max_total: int) -> List[Dict[str, object]]:
    ranked = sorted(
        parsed,
        key=lambda x: (str(x.get("date", "")), int(x.get("_score", 0))),
        reverse=True,
    )

    selected: List[Dict[str, object]] = []
    seen_fact: Set[str] = set()
    for item in ranked:
        key = compact_key(str(item.get("fact", "")))
        if not key or key in seen_fact:
            continue
        seen_fact.add(key)
        selected.append(item)
        if len(selected) >= max_total:
            break

    selected.sort(key=lambda x: (str(x.get("date", "")), str(x.get("fact", ""))), reverse=True)
    compact: List[Dict[str, object]] = []
    for item in selected:
        compact.append(
            {
                "date": str(item.get("date", "")),
                "fact": str(item.get("fact", "")),
                "source": str(item.get("source", "")),
                "tags": list(item.get("tags", [])),
            }
        )
    return compact


def load_existing_items() -> List[Dict[str, object]]:
    if not ITEMS_FILE.exists():
        return []
    text = ITEMS_FILE.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []

    sanitized: List[Dict[str, object]] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        date = str(row.get("date", "")).strip()
        fact = str(row.get("fact", "")).strip()
        source = str(row.get("source", "")).strip()
        tags_raw = row.get("tags", [])
        tags: List[str] = []
        if isinstance(tags_raw, list):
            tags = [str(tag).strip() for tag in tags_raw if str(tag).strip()]
        elif isinstance(tags_raw, str) and tags_raw.strip():
            tags = [tags_raw.strip()]

        if date and fact and source:
            sanitized.append(
                {
                    "date": date,
                    "fact": fact,
                    "source": source,
                    "tags": tags,
                }
            )
    return sanitized


def save_items(items: List[Dict[str, object]]) -> None:
    ITEMS_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def diff_counts(prev: List[Dict[str, object]], curr: List[Dict[str, object]]) -> Tuple[int, int, int]:
    def key(item: Dict[str, object]) -> str:
        return f"{item.get('date', '')}|{item.get('fact', '')}|{item.get('source', '')}"

    prev_map = {key(item): tuple(item.get("tags", [])) for item in prev}
    curr_map = {key(item): tuple(item.get("tags", [])) for item in curr}

    prev_keys = set(prev_map.keys())
    curr_keys = set(curr_map.keys())
    inserted = len(curr_keys - prev_keys)
    removed = len(prev_keys - curr_keys)
    updated = sum(1 for k in (curr_keys & prev_keys) if curr_map[k] != prev_map[k])
    return inserted, updated, removed


def build_summary(items: List[Dict[str, object]], scanned_files: int, days: int, max_per_file: int, max_total: int) -> str:
    tag_counter: Counter[str] = Counter()
    for item in items:
        for tag in item.get("tags", []):
            tag_counter[str(tag)] += 1

    lines: List[str] = [
        "# High-Value Capsules Summary",
        "",
        f"- 扫描窗口：最近 {days} 天",
        f"- 扫描文件数：{scanned_files}",
        f"- 每文件上限：{max_per_file}",
        f"- 总条目上限：{max_total}",
        f"- 当前条目数：{len(items)}",
        "- 字段：`date/fact/source/tags`",
        "",
        "## 标签分布",
    ]

    if not tag_counter:
        lines.append("- 暂无")
    else:
        for tag, count in tag_counter.most_common():
            lines.append(f"- {tag}：{count}")

    lines.extend(
        [
            "",
            "## 最近高价值原子信息（Top 30）",
        ]
    )
    preview = items[:30]
    if not preview:
        lines.append("- 暂无")
    else:
        for item in preview:
            tag_view = ",".join(item.get("tags", []))
            lines.append(f"- [{item.get('date', '')}] {item.get('fact', '')} [{tag_view}]")

    lines.extend(
        [
            "",
            "## 使用建议",
            "- 周复盘优先读取本摘要，不直接读取全量 `items.json`。",
            "- 新结论优先回写 `memory/MEMORY.md`，避免层级混乱。",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    ensure_layout()

    candidates = list_candidate_files(args.days)
    current_fingerprint = fingerprint(candidates, args.days, args.max_per_file, args.max_total)
    state = read_state()

    if not args.force and state.get("fingerprint") == current_fingerprint:
        print("[SKIP] 外部源无新增改动，跳过高价值提取")
        print(f"[SKIP] State file: {STATE_FILE}")
        return

    previous_items = load_existing_items()
    parsed_items: List[Dict[str, object]] = []
    for file_path in candidates:
        parsed_items.extend(parse_file(file_path, max_per_file=args.max_per_file))

    compact_items = select_compact_capsules(parsed_items, max_total=max(1, args.max_total))
    inserted, updated, removed = diff_counts(previous_items, compact_items)

    save_items(compact_items)
    SUMMARY_FILE.write_text(
        build_summary(
            compact_items,
            scanned_files=len(candidates),
            days=args.days,
            max_per_file=args.max_per_file,
            max_total=args.max_total,
        ),
        encoding="utf-8",
    )

    write_state(
        {
            "updated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fingerprint": current_fingerprint,
            "days": args.days,
            "max_per_file": args.max_per_file,
            "max_total": args.max_total,
            "scanned_files": len(candidates),
            "parsed_candidates": len(parsed_items),
            "total_items": len(compact_items),
        }
    )

    print(f"[OK] 扫描文件: {len(candidates)}")
    print(f"[OK] 高价值候选: {len(parsed_items)}")
    print(f"[OK] items: +{inserted} inserted, {updated} updated, -{removed} removed, {len(compact_items)} total")
    print(f"[OK] 输出: {ITEMS_FILE}")
    print(f"[OK] 输出: {SUMMARY_FILE}")
    print(f"[OK] 状态: {STATE_FILE}")


if __name__ == "__main__":
    main()
