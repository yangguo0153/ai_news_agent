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
- 证据：`/Users/will/Desktop/通往AGI之路/agent-engineer` 已按该结构落地，并包含公众号与抖音双渠道模板。
- 来源：本次交付（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.97
- 状态：superseded
- 被替代说明：已升级为“三层记忆 + 双脚本自动化”结构（见条目10）。

### 6) 周复盘自动化模式
- 结论：周复盘最小自动化应包含“日志聚合脚本 + 3内容生成 Prompt + 发布计划模板”。
- 证据：`run_weekly_review.sh` 可自动汇总最近7日日志并产出 `weekly_input_pack.md` 与 `publish_plan.md`。
- 来源：本次实测（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.99
- 状态：superseded
- 被替代说明：已升级为“Layer1/2/3 联合聚合”的周复盘引擎（见条目11）。

### 7) 业务文档迁移收口模式
- 结论：处理大批业务文档变更时，先按目录分组确认，再按组提交能显著降低误提交风险。
- 证据：本次按“项目交接包删除 + 媒体管理系统新增”两组收口并提交 `3ffda47`，目标路径状态已清空。
- 来源：本次执行（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.98
- 状态：active

### 8) 工作区杂乱治理优先级
- 结论：清理应采用 P0/P1/P2 分层决策：先删噪声，再提交结构性删除，最后处理体量大但可重建产物（如 `.venv`）。
- 证据：`workspace/workspace_cleanup_review_2026-02-24.md` 的统计显示 `文案部/.venv` 319M、`.DS_Store` 19 个、当前 Git 实际待决策改动仅 1 项（gitlink 删除）。
- 来源：本次复盘（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.97
- 状态：active

### 9) 规则层冲突检测结果
- 结论：Global Baseline（系统设置）与项目 `AGENTS.md`（仓库）无硬冲突，可并行；当前问题是“重复约束较多”，但不影响执行正确性。
- 证据：两层规则均要求“先计划、后执行、完成验证、记忆沉淀”，且未出现互斥条件。
- 来源：重启后规则审计（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.98
- 状态：active

### 10) Agent Engineer 深度架构升级
- 结论：`agent-engineer` 已从“模板集合”升级为“3层记忆（areas/daily/MEMORY）+ 渐进式读取 + 自动沉淀脚本”的复利工作区。
- 证据：新增 `agent-engineer/memory/INDEX.md`、`PROFILE.md`、`MEMORY.md`、`memory/areas/**`，并落地 `pipeline/ingest_daily_log.py` 与 `run_daily_ingest.sh`。
- 来源：本次执行（2026-02-24，基于用户提供文章思路）。
- 日期：2026-02-24
- 置信度：0.98
- 状态：active

### 11) 周复盘引擎升级为三层消费
- 结论：周复盘脚本已升级为直接消费 Layer1/Layer2/Layer3，周输入包不再只拼接原始日志，内容一致性与可追溯性显著提升。
- 证据：新增 `agent-engineer/pipeline/build_weekly_context.py`，执行 `bash agent-engineer/pipeline/run_weekly_review.sh 7` 生成 `outputs/weekly/2026-W09/weekly_input_pack.md`，其中含三层记忆分区。
- 来源：本次命令验证（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.99
- 状态：active

### 12) 抗 FOMO 的问题驱动学习法（内容选题）
- 结论：对抗 2026 年的 FOMO，更有效的方法是“少装工具、多做验证”：把学习从工具清单改成问题清单，用 20 分钟验证门槛 + 30 分钟闭环推进真实进展。
- 证据：在 `agent-engineer` 内产出公众号文章 `outputs/wechat/2026-02-24_化繁为简_对抗FOMO.md`，并补强为可复制干货（20 分钟验证卡片 / 问 AI 提示词 / worktree 保险箱命令），同时回写到 `agent-engineer/memory/MEMORY.md` 与 `memory/daily/2026-02-24.md`。
- 来源：本次内容生产与回写（2026-02-24）。
- 日期：2026-02-24
- 置信度：0.96
- 状态：active

### 13) 微信原文写作工作流抽象（XvFZ 链接）
- 结论：该文可复用框架可归纳为“两层判断机制 + 9步写作流程 + 7个协作要点”，核心目标是让写作协作“可预测、可追溯、可控”。
- 证据：直接抓取 `https://mp.weixin.qq.com/s/XvFZtoybx_u_W8Os4eQdlQ` 的正文并提取到 `/tmp/wechat_article_XvFZ.txt`，关键结构完整出现（工作区判断、任务类型判断、Step1-9、Think Aloud、三遍审校、可复制/不可复制边界）。
- 来源：本次原文解析与结构化提炼（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.97
- 状态：active

### 14) 枯荣IP Skill 初版已落地并可执行
- 结论：`kurong-ip` Skill 已完成从模板到可执行初版，包含规则定义、流程参考、审校清单与工作区初始化脚本，可直接启动个人IP写作自动化协作。
- 证据：新增目录 `.agent/skills/kurong-ip/`，包含 `SKILL.md`、`agents/openai.yaml`、`references/{workflow.md,style-review-checklist.md,article-insights.md}`、`scripts/bootstrap_workspace.py`；执行 `quick_validate.py` 返回 `Skill is valid!`，脚本实测在 `/tmp/kurong-ip-demo.*` 成功创建标准目录与模板文件。
- 来源：本次执行与命令验证（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.99
- 状态：superseded
- 被替代说明：已迁移到全局目录 `/Users/will/.codex/skills/kurong-ip`（见条目20）。

### 15) 产物可见性保障（绝对路径策略）
- 结论：为避免编辑器误开同名文件，产物汇报必须使用绝对路径；并让脚手架输出“绝对路径 + 文件大小”用于即时验真。
- 证据：本次已在 `AGENTS.md` 增加绝对路径规则，`bootstrap_workspace.py` 输出改造已实测，且新增 `.agent/skills/kurong-ip/FILEMAP.md` 作为点击入口。
- 来源：本次排查与修复（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.98
- 状态：superseded
- 被替代说明：入口清单已迁移到 `/Users/will/.codex/skills/kurong-ip/FILEMAP.md`（见条目20）。

### 16) 编辑器短文件名兜底策略（同名软链接）
- 结论：当 Antigravity/Cursor 仍会把短文件名映射错路径时，根目录同名软链接是稳定兜底方案，可保证“点短名也打开真实文件”。
- 证据：根目录已新增并验证 `SKILL.md`、`workflow.md`、`style-review-checklist.md`、`article-insights.md`、`bootstrap_workspace.py`、`openai.yaml` 6 个软链接，全部解析到 `.agent/skills/kurong-ip/` 对应文件且文件内容可读。
- 来源：本次排查与修复（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.99
- 状态：superseded
- 被替代说明：软链接目标已改为全局目录 `/Users/will/.codex/skills/kurong-ip`（见条目20）。

### 17) 枯荣IP 人格卡标准化
- 结论：`kurong-ip` 已具备可复用的人格卡规范（身份/价值观/语气/禁区/证据标准/人机边界），并接入执行流程，后续写作可默认按该人格输出。
- 证据：新增 `.agent/skills/kurong-ip/references/persona-card.md`；`SKILL.md` 增加引用；`references/workflow.md` Step 5 明确“先读取人格卡再学习风格”；`quick_validate.py` 校验通过。
- 来源：本次实现与命令验证（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.99
- 状态：superseded
- 被替代说明：人格卡文件已迁移到 `/Users/will/.codex/skills/kurong-ip/references/persona-card.md`（见条目20）。

### 18) 非 ASCII 路径点击兼容策略（ASCII 链接层）
- 结论：当工作区路径包含中文时，聊天中默认提供 ASCII 绝对路径（`/tmp/agi-road-links/...`）作为点击入口，可避免 URL 编码不反解导致的空白文件打开问题。
- 证据：`/tmp/agi-road-links/` 下链接已实测：`SKILL.md/workflow.md/persona-card.md/openai.yaml/MEMORY.md/2026-02-25.md` 均非空且解析到真实文件；`CLICK_OPEN_FILES.md` 已更新“Recommended (ASCII Safe Paths)”。
- 来源：本次排查与修复（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.99
- 状态：active

### 19) ASCII 链接层的完整性要求（清单文件也必须建链接）
- 结论：`/tmp/agi-road-links/` 不仅要覆盖业务文件，还必须覆盖入口清单文件本身（`CLICK_OPEN_FILES.md`）；否则用户点击清单会误判为“文件空白”。
- 证据：故障时 `/tmp/agi-road-links/CLICK_OPEN_FILES.md` 缺失；补建软链接后 `wc -c /tmp/agi-road-links/CLICK_OPEN_FILES.md` 为 1840 字节，正文可读，问题复现消失。
- 来源：本次排查与修复（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.99
- 状态：active

### 20) kurong-ip 全局安装与旧路径清理
- 结论：`kurong-ip` 已正式安装到全局目录 `/Users/will/.codex/skills/kurong-ip`，并按用户要求删除原路径 `.agent/skills/kurong-ip`。
- 证据：`cp -R` 后 `quick_validate.py /Users/will/.codex/skills/kurong-ip` 返回 `Skill is valid!`；旧路径检查为 `OLD_REMOVED`；根目录 7 个同名软链接已重定向至全局路径。
- 来源：本次迁移执行与验证（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.99
- 状态：active

## Superseded Knowledge
- 暂无

## Reusable Patterns
- 先建立固定记忆结构，再在任务结束时沉淀高价值结论。
- 采用“索引优先、按需读取”减少上下文开销。
- 将外部方法论先拆解为“可复制机制/不可复制资产”，再转写为 Skill 的路由、流程、闸门与脚本。
- 将“人格卡”从文案偏好升级为流程依赖，先锁定边界再写作，可显著降低风格漂移。

## Last Updated
- 2026-02-25
