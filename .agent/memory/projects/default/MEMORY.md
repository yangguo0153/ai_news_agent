# Default Project Memory

## Active Knowledge

### 1) 协作机制
- 结论：采用“最小 AGENTS 保底 + 全局记忆 Skill”。
- 证据：用户确认“按推荐执行”。
- 来源：会话决策（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.98
- 状态：active

### 2) 全局能力落地状态
- 结论：`memory-compound` 全局 Skill 已安装到 `~/.codex/skills/memory-compound`。
- 证据：目录下 `SKILL.md`、`agents/openai.yaml`、`references/memory_schema.md` 均存在。
- 来源：本次执行结果（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.97
- 状态：active

### 3) worktree 与 AGENTS 行为
- 结论：`AGENTS.md` 若未提交，仅在当前工作区可见；新建 `worktree` 默认检出不到该文件。
- 证据：`codex/agents-check` worktree 初始缺失 `AGENTS.md`，手动同步后恢复为 1310 字节。
- 来源：本次 worktree 校验（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.98
- 状态：active

### 4) 提交后继承行为
- 结论：将 `AGENTS.md` 与 `.agent/memory` 提交到 `main` 后，新建 worktree 会自动继承这些文件。
- 证据：提交 `84b2c89` 后创建 `codex/agents-check-v2`，无需手动拷贝即包含完整文件集。
- 来源：本次提交与验证（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.99
- 状态：active

### 5) 内容变现工作区模板
- 结论：内容型 workspace 的最小有效结构为 `inputs + prompts + outputs + pipeline + templates`。
- 证据：`/Users/will/Desktop/agent-engineer` 已按该结构落地，并包含公众号与抖音双渠道模板。
- 来源：本次交付（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.97
- 状态：active

### 6) 周复盘自动化模式
- 结论：周复盘最小自动化应包含“日志聚合脚本 + 3内容生成 Prompt + 发布计划模板”。
- 证据：`run_weekly_review.sh` 可自动汇总最近7日日志并产出 `weekly_input_pack.md` 与 `publish_plan.md`。
- 来源：本次实测（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.99
- 状态：active

## Superseded Knowledge
- 暂无

## Reusable Patterns
- 先建立固定记忆结构，再在任务结束时沉淀高价值结论。
- 采用“索引优先、按需读取”减少上下文开销。

## Last Updated
- 2026-02-24
