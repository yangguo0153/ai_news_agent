# Workflow

## 日更循环（Daily Loop）

1. 输入
- 在 `inputs/daily_logs/YYYY-MM-DD.md` 记录当日动作、证据与结果。

2. 自动沉淀（推荐入口）
- 运行 `bash pipeline/run_memory_sync.sh`
- 自动识别并更新：
  - `memory/daily/YYYY-MM-DD.md`
  - `memory/areas/**/items.json`
  - `memory/areas/**/summary.md`
  - `memory/.state/*.json`
- 外部源仅沉淀高价值胶囊（字段固定：`date/fact/source/tags`）

3. 内容生成
- 基于 `prompts/summary_to_content_brief.md` 产出内容简报
- 再生成公众号和抖音内容

4. 质检
- 对照 `pipeline/quality_checklist.md`

5. 反馈
- 发布后把阅读、互动、私信数据写进下一次 daily log

## 周循环（Weekly Loop）

1. 运行 `bash pipeline/run_weekly_review.sh`
2. 自动生成周输入包和发布计划
3. 用周提示词生成 3 条内容（深度文 + 口播 + 二次分发）
4. 复盘“内容 -> 线索 -> 转化”链路
