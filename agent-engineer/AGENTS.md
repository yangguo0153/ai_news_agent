---
trigger: always_on
alwaysApply: true
---

# Agent Engineer 执行协议

## 目标
- 让内容生产从“临时发挥”升级为“记忆复利系统”。

## 强制流程
1. 先读：`memory/INDEX.md` -> `memory/PROFILE.md` -> `memory/MEMORY.md`
2. 生产前按需读：相关 `memory/areas/*/*/summary.md`
3. 生成后必须回写：
   - `inputs/daily_logs/*.md`（当天记录）
   - `memory/daily/YYYY-MM-DD.md`（结构化沉淀）
   - 必要时更新 `memory/MEMORY.md`
4. 任务涉及内容改动时，执行 `bash pipeline/run_memory_sync.sh`：
   - 自动判断 `inputs/daily_logs` 是否需要重新 ingest
   - 自动判断外部知识源是否有增量并提取原子关系

## 外部知识源（本地提取）
- `/Users/will/Desktop/通往AGI之路`：仅读取日志/总结/进度/记忆类文档（最近 90 天）
- `/Users/will/Library/Mobile Documents/iCloud~md~obsidian/Documents/我有一个想法1.1/99_Daily`：读取最近 90 天日记
- 提取结果必须保持精简：仅高价值条目（洞察/里程碑/失败复盘/奇思妙想）
- `items.json` 字段固定为：`date/fact/source/tags`

## 写作标准
- 结论先行，案例可验证。
- 不写无证据战绩。
- 每条内容都要有明确 CTA。

## 记忆标准
- 事实写入 `items.json`，字段至少包含：
  - `id` `date` `fact` `evidence` `source` `confidence` `status`
- 覆盖旧结论时标记 `superseded`，禁止直接删除。
