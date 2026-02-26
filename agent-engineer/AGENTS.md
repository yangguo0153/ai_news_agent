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
- `/Users/will/Desktop/RoadToAGI`：仅读取日志/总结/进度/记忆类文档（最近 90 天）
- `/Users/will/Library/Mobile Documents/iCloud~md~obsidian/Documents/我有一个想法1.1/99_Daily`：读取最近 90 天日记
- 提取结果必须保持精简：仅高价值条目（洞察/里程碑/失败复盘/奇思妙想）
- `items.json` 字段固定为：`date/fact/source/tags`

## 写作标准
- 结论先行，案例可验证。
- 不写无证据战绩。
- 每条内容都要有明确 CTA。

## 路径展示标准（强制）
- 交付路径只允许固定格式：先写原文件名（纯文本），下一行写单反引号包裹的原始绝对路径（纯文本）。
- 路径必须是当前真实磁盘路径，不做任何别名替换、编码替换或额外入口文件生成。
- 禁止使用任何本地 Markdown 链接语法（如 `[file](本地路径)`）或其他可点击本地链接写法。
- 禁止输出“裸文件名列表”作为交付（如 `- assignment_A.md`）；文件名必须作为纯文本说明出现。
- 历史对话与历史记忆中的其他路径格式一律视为已废弃，不再复用。

## 记忆标准
- 内部记忆（daily ingest 生成的各 area `items.json`）字段：`id` `date` `fact` `evidence` `source` `confidence` `status`
- 外部高价值胶囊（`memory/areas/profile/subject-object-actions/items.json`）字段：`date` `fact` `source` `tags`
- 覆盖旧结论时标记 `superseded`，禁止直接删除。
- 读取记忆出现冲突时，只采纳“最新日期 + `status: active`”结论；`superseded` 与历史 daily 条目仅作审计，不作执行指令。
