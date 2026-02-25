# Durable Memory (Layer 3)

## Active Knowledge

### 1) 双渠道复用策略
- ID: `mem-24a2f9b1f1`
- 结论：同一份周输入包应先产出公众号深度稿，再拆成抖音口播脚本，最后做短分发。
- 证据：同源素材复用可降低内容生产成本并保持观点一致。
- 来源：工作区设计决策。
- 日期：2026-02-24
- 置信度：0.90
- 状态：active

### 2) 证据优先发布标准
- ID: `mem-b9629982df`
- 结论：任何内容必须能追溯到 daily log、项目输出或可验证反馈。
- 证据：无证据内容会降低信任与转化质量。
- 来源：内容生产规则。
- 日期：2026-02-24
- 置信度：0.93
- 状态：active


### 3) 内容型 Agent 工作区要长期有效，必须把“每...
- ID: `mem-d7cddd73a5`
- 结论：内容型 Agent 工作区要长期有效，必须把“每日事实沉淀”自动化，而不是依赖手工整理。
- 证据：今天新增 ingest_daily_log.py 并接入 run_daily_ingest.sh。
- 来源：inputs/daily_logs/2026-02-24.md
- 日期：2026-02-24
- 置信度：0.92
- 状态：active

### 4) 周复盘应直接消费三层记忆（areas + dai...
- ID: `mem-655ad8433e`
- 结论：周复盘应直接消费三层记忆（areas + daily + MEMORY），否则周内容会失真。
- 证据：今天用 build_weekly_context.py 替换旧版拼接脚本。
- 来源：inputs/daily_logs/2026-02-24.md
- 日期：2026-02-24
- 置信度：0.88
- 状态：active

### 5) 对抗 FOMO 的有效方式是把学习从“工具清单”...
- ID: `mem-da6e10fce7`
- 结论：对抗 FOMO 的有效方式是把学习从“工具清单”改成“问题清单”：遇到具体项目就查攻略并立刻验证。
- 证据：今天围绕 Git worktree 的实际需求，查基础命令/原理后直接实操并完成清理验证。
- 来源：inputs/daily_logs/2026-02-24.md
- 日期：2026-02-24
- 置信度：0.9
- 状态：active

### 6) 在 AI 辅助开发中，用 `git worktr...
- ID: `mem-8387486f3d`
- 结论：在 AI 辅助开发中，用 `git worktree` 隔离实验能显著降低“AI 发疯”带来的损失，把试错成本降到可控。
- 证据：今天的 detached 临时 worktree 在强制关闭后被清理，主工作区保持稳定。
- 来源：inputs/daily_logs/2026-02-24.md
- 日期：2026-02-24
- 置信度：0.85
- 状态：active

### 7) 外部知识源抽取应走“增量指纹”机制
- ID: `mem-bb1ea73f44`
- 结论：外部日志类知识源提取应通过状态指纹判断是否重跑，否则会导致重复抽取和维护成本上升。
- 证据：新增 `pipeline/ingest_external_atomic.py` 后，`bash pipeline/run_memory_sync.sh` 在无变更时可稳定 skip。
- 来源：memory/daily/2026-02-25.md
- 日期：2026-02-25
- 置信度：0.94
- 状态：active

### 8) 统一入口可显著降低记忆漏写风险
- ID: `mem-19554ed649`
- 结论：将 `daily ingest + external ingest` 合并到统一入口 `run_memory_sync.sh`，比人工判断更可靠。
- 证据：新增 `pipeline/auto_memory_sync.py` 后，一次命令即可自动识别是否需要重跑两类沉淀流程。
- 来源：memory/daily/2026-02-25.md
- 日期：2026-02-25
- 置信度：0.91
- 状态：active

### 9) 外部原子层必须“少而精”，字段固定为四项
- ID: `mem-8c405a7e12`
- 结论：外部知识源原子信息默认只保留 `date/fact/source/tags`，并通过“每文件2条、总量60条”约束防止信息爆炸。
- 证据：`ingest_external_atomic.py` 已升级为高价值胶囊筛选；`run_external_ingest.sh --days 90 --force` 输出压缩为 49 条。
- 来源：memory/daily/2026-02-25.md
- 日期：2026-02-25
- 置信度：0.96
- 状态：active
## Superseded Knowledge
- 暂无

## Last Updated
- 2026-02-25
