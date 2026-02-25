# Agent Engineer Workspace

这个工作区不是“提示词仓库”，而是一个内容复利引擎。

目标：把你每天的 vibe coding / 项目开发过程，自动沉淀为
- 公众号文章（深度）
- 抖音口播脚本（传播）
- 可转化动作（私信/咨询/资料领取）

## 核心架构（三层记忆）

1. Layer 1 知识图谱（可搜索）
- `memory/areas/**/items.json`：原子事实
- `memory/areas/**/summary.md`：动态摘要

2. Layer 2 每日时间线（可追溯）
- `memory/daily/YYYY-MM-DD.md`

3. Layer 3 隐性知识（可复用）
- `memory/MEMORY.md`

原则：旧结论不删，只做 `superseded`。

## 每日 10 分钟流程

1. 写日志：复制 `templates/daily_log_template.md` 到 `inputs/daily_logs/YYYY-MM-DD.md`
2. 记忆沉淀：`bash pipeline/run_memory_sync.sh`（自动识别是否需要重跑）
3. 内容生成：
- 公众号：`prompts/wechat_article_prompt.md`
- 抖音：`prompts/douyin_script_prompt.md`
4. 质检：`pipeline/quality_checklist.md`
5. 记录反馈：把数据回写到下一次 daily log

## 外部知识源（自动增量）

- 源1：`/Users/will/Desktop/通往AGI之路`（仅日志/总结/进度/记忆类文档）
- 源2：`/Users/will/Library/Mobile Documents/iCloud~md~obsidian/Documents/我有一个想法1.1/99_Daily`
- 时间窗：最近 90 天
- 高价值筛选：只保留洞察、里程碑、失败复盘、奇思妙想
- 字段模型：`date/fact/source/tags`
- 控制上限：每文件最多 2 条，最终最多 60 条
- 输出位置：`memory/areas/profile/subject-object-actions/items.json`

## 数据边界

- 提取脚本仅在本地文件系统运行，不上传外部知识源文件。

## 每周 30 分钟流程

1. 运行：`bash pipeline/run_weekly_review.sh`
2. 自动生成：
- `outputs/weekly/YYYY-Www/weekly_input_pack.md`
- `outputs/weekly/YYYY-Www/publish_plan.md`
3. 用 `prompts/weekly_recap_to_3_contents_prompt.md` 一次生成 3 条可发布内容

## 目录说明

- `inputs/daily_logs/`：原始日志输入
- `memory/`：三层记忆系统（核心）
- `prompts/`：内容生成提示词
- `pipeline/`：自动化脚本与执行规范
- `outputs/`：每周与渠道产物
- `templates/`：模板

## 最小命令

```bash
# 每日/外部统一沉淀（自动增量识别）
bash pipeline/run_memory_sync.sh

# 仅外部知识源提取（默认最近90天）
bash pipeline/run_external_ingest.sh --days 90

# 每周聚合（自动生成周输入包）
bash pipeline/run_weekly_review.sh
```
