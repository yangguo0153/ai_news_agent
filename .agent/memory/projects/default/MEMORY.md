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
- 证据：`/Users/will/Desktop/RoadToAGI/agent-engineer` 已按该结构落地，并包含公众号与抖音双渠道模板。
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
- 状态：superseded
- 被替代说明：已切换为固定根别名 `/Users/will/Desktop/agi-road/...`（见条目24），不再按文件维护 `/tmp/agi-road-links/*`。

### 19) ASCII 链接层的完整性要求（清单文件也必须建链接）
- 结论：`/tmp/agi-road-links/` 不仅要覆盖业务文件，还必须覆盖入口清单文件本身（`CLICK_OPEN_FILES.md`）；否则用户点击清单会误判为“文件空白”。
- 证据：故障时 `/tmp/agi-road-links/CLICK_OPEN_FILES.md` 缺失；补建软链接后 `wc -c /tmp/agi-road-links/CLICK_OPEN_FILES.md` 为 1840 字节，正文可读，问题复现消失。
- 来源：本次排查与修复（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.99
- 状态：superseded
- 被替代说明：`/tmp/agi-road-links/*` 链接层已降级为应急方案；默认改用固定根别名 `/Users/will/Desktop/agi-road/...`（见条目24）。

### 20) kurong-ip 全局安装与旧路径清理
- 结论：`kurong-ip` 已正式安装到全局目录 `/Users/will/.codex/skills/kurong-ip`，并按用户要求删除原路径 `.agent/skills/kurong-ip`。
- 证据：`cp -R` 后 `quick_validate.py /Users/will/.codex/skills/kurong-ip` 返回 `Skill is valid!`；旧路径检查为 `OLD_REMOVED`；根目录 7 个同名软链接已重定向至全局路径。
- 来源：本次迁移执行与验证（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.99
- 状态：active

### 21) 历史分支关闭判定与清理已执行
- 结论：对“截图中疑似 worktree 分支”完成清理：凡已被 `main` 包含且不被 worktree 占用的分支可直接删除；本次已删除 5 个历史分支。
- 证据：`git branch -d codex/agents-check-v2 codex/agents-check phase3-interaction worktree-cheeky-frolicking-nova worktree-feature-work` 全部成功；当前 `git branch -vv` 仅剩 `main` 和 `codex/quality-optimization-v1`（该分支被 `/private/tmp/wenanbu-quality-opt` 占用）。
- 来源：本次分支清理执行（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.99
- 状态：active

### 22) 分支清理后的提交流程焦点
- 结论：清理历史分支后，提交流程应聚焦 `main` 的未跟踪文件，不再以“历史 worktree 进度”作为阻塞条件。
- 证据：`git status` 仅显示 `文案部/.agent/memory/INDEX.md`、`PROFILE.md`、`daily/2026-02-25.md`、`projects/default/MEMORY.md` 四个未跟踪文件。
- 来源：本次状态复核（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.98
- 状态：active

### 23) ai_news_agent 的 DeepSeek 变量切换策略
- 结论：`ai_news_agent` 已切换为 `DEEPSEEK_*` 作为主配置入口，同时在运行时回填 `OPENAI_*` 以兼容 CrewAI/LiteLLM 的 OpenAI 兼容模式，避免仅改 secret 名称导致启动失败。
- 证据：`.github/workflows/daily_news.yml` 已改为 `secrets.DEEPSEEK_API_KEY/DEEPSEEK_API_BASE/DEEPSEEK_MODEL_NAME`；`main.py` 增加 `DEEPSEEK_* -> OPENAI_*` 归一化逻辑；`crew.py` 改为优先读取 `DEEPSEEK_*`；`python3 -m compileall src/ai_news_agent` 通过。
- 来源：本次实现与命令验证（2026-02-25）。
- 日期：2026-02-25
- 置信度：0.99
- 状态：active

### 24) 路径点击体验修复为“固定 ASCII 根别名”
- 结论：为避免中文根路径导致的点击打开失败，默认可点击路径已统一为 `/Users/will/Desktop/agi-road/...`，并禁用“每文件临时 `/tmp/agi-road-links/*`”作为常规流程。
- 证据：`/Users/will/Desktop/agi-road -> /Users/will/Desktop/RoadToAGI` 软链接已创建并可解析；别名路径下 `AGENTS.md`、`memory/INDEX.md`、`memory/projects/default/MEMORY.md` 均验证可读且非空；`AGENTS.md` 交付规则已更新为“固定别名单路径优先”。
- 来源：本次执行与命令验证（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.98
- 状态：superseded
- 被替代说明：已升级为跨工作区全局别名层 `/Users/will/.codex/path-aliases/*`（见条目25）。

### 25) 空白文件根因与全局路径修复（跨工作区）
- 结论：空白文件的根因是点击了短文件名而非绝对路径，导致编辑器在当前工作区新建空文件；修复应放在全局层：统一使用 `~/.codex/path-aliases` 的 ASCII 绝对路径并禁用短名链接。
- 证据：截图文件 `09-人机协同试运行方案_v1.md` 在磁盘无匹配；新增 `/Users/will/.codex/scripts/ensure_workspace_aliases.sh` 可根据 `.codex-global-state.json` 生成工作区别名与 `current-workspace`；`/Users/will/.codex/AGENTS.md` 已新增 `delivery.file_links` 规则（强制 Markdown 绝对路径、禁短名、缺失先刷新别名）。
- 来源：本次排查与实现（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.97
- 状态：superseded
- 被替代说明：发现客户端还会错误使用中文 label 并编码成 `%E9...` 文件名；已升级为“ASCII 别名文件 + ASCII label/href 同名”策略（见条目26）。

### 26) `%E9...` 空白页的稳定规避：ASCII 别名文件机制
- 结论：当客户端把中文 label 编码并按本地文件名打开时，路径别名本身不足以修复；稳定方案是为目标文件生成固定 `open-<hash>.<ext>` 软链接，并在 Markdown 中让 label 与 href 都使用同一 ASCII 别名。
- 证据：新增 `.agent/scripts/register_click_alias.sh`、`.agent/click-alias/{WORKSPACES.txt,INDEX.tsv,README.md}`；注册后 `open-7efce8e3ba.md` 与 `open-5c642a7cb5.md` 在多个工作区根目录可解析且可读，源文件内容未复制。
- 来源：本次复现与实现（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.98
- 状态：superseded
- 被替代说明：已升级为“原文件名纯文本展示 + ASCII 别名点击 + 统一报告索引入口”（见条目27）。

### 27) 报告可见性标准化：原名展示 + 单入口索引
- 结论：为了兼顾“原文件名可读性”和“稳定可点击”，交付格式应固定为“原文件名（纯文本）+ ASCII 别名打开链接”；并统一提供 `open-report-index.md` 作为报告入口，避免找不到文件。
- 证据：`register_click_alias.sh` 已自动生成 `.agent/click-alias/REPORT_INDEX.md`，并在各工作区根目录创建 `open-report-index.md` 软链接；`AGENTS.md` 已更新交付规则（禁止中文可点击 label，要求原名展示）。
- 来源：本次实现与验证（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.98
- 状态：superseded
- 被替代说明：用户明确要求彻底放弃 ASCII 临时入口；已改为“原路径直出 + URL 编码路径兼容映射”（见条目28）。

### 28) 原路径直出策略：URL 编码路径兼容映射
- 结论：当前最符合用户诉求且可稳定落地的方案是保留“原文件名 + 原始绝对路径”展示，同时在文件系统自动创建 `%E9...` 编码路径到真实路径的软链接映射，避免客户端编码后打开空白文件。
- 证据：新增 `.agent/scripts/register_urlencoded_path_aliases.sh`；执行后已创建 `/Users/will/Desktop/%E9%80%9A%E5%BE%80AGI%E4%B9%8B%E8%B7%AF -> /Users/will/Desktop/RoadToAGI` 以及 `文案部/00-重启调研` 下对应编码文件名映射；通过编码绝对路径 `sed` 可读取真实内容。
- 来源：本次实现与命令验证（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.96
- 状态：superseded
- 被替代说明：用户拒绝编码映射带来的系统冗余，已回退并移除映射层（见条目30）。

### 29) 全局规则收口：停止 ASCII 临时入口
- 结论：为避免跨会话回退，全局 `~/.codex/AGENTS.md` 已切换为“原路径直出 + URL 编码映射兼容”策略，不再引导 ASCII 临时入口。
- 证据：`/Users/will/.codex/AGENTS.md` 的 `delivery.file_links` 已改写，且 JSON 校验通过。
- 来源：本次配置更新与验证（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.97
- 状态：superseded
- 被替代说明：全局规则已进一步收口为“纯文本原始绝对路径 + 禁止 Markdown 本地链接 + 禁止编码映射”（见条目30）。

### 30) 最终路径策略：纯文本原路径（无 ASCII/无编码映射）
- 结论：按用户最终要求，路径交付统一为“原文件名 + 单反引号纯文本绝对路径”，彻底禁用 ASCII 临时入口和 `%E9...` 编码映射兼容层。
- 证据：项目 `AGENTS.md` 已改为禁止 Markdown 本地链接与所有临时入口；已删除 `.agent/scripts/register_click_alias.sh`、`.agent/click-alias/`、`.agent/scripts/register_urlencoded_path_aliases.sh`，并清理 `/Users/will/Desktop/agi-road`、`/Users/will/Desktop/%E9%80%9A%E5%BE%80AGI%E4%B9%8B%E8%B7%AF`、`~/.codex/path-aliases`、`~/.codex/scripts/ensure_workspace_aliases.sh`；全局 `~/.codex/AGENTS.md` 已同步到同一策略。
- 来源：本次回退与验证（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.98
- 状态：superseded
- 被替代说明：已收敛到条目37的“根治版单一执行模板（含禁裸文件名列表）”。

### 31) /private/tmp 清理边界（仅删项目残留，不动系统项）
- 结论：`/private/tmp` 可视为临时目录，但清理应采用白名单方式：仅删除项目实验与日志残留，保留系统 socket / IPC / `com.apple*` 等运行时项。
- 证据：本次已删除 `agi-road-links`、`kurong-ip-*`、`wechat_article*`、`alias_run.log`、`register_alias_debug.log`、`urlalias_sync.log`、`wt-cleanup-backups` 等；清理后 `du -sh /private/tmp` 为 `204K`，且仅剩系统/应用运行项与少量零字节文件。
- 来源：本次命令清理与复核（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.99
- 状态：active

### 32) 仓库冗余治理优先级（2026-02-26 复核）
- 结论：本仓库当前冗余治理应按 P0/P1 执行：P0 先处理 `文案部/_archive/reset_2026-02-25/legacy_runtime/.venv`（约 319M，最高收益）；P1 再清理全仓 `.DS_Store`（24 个）与非必要日志/零字节文件。
- 证据：`du -h -d 3` 显示仓库总量约 402M，其中 `文案部` 322M、`文案部/_archive` 320M、`legacy_runtime/.venv` 319M；`find . -name '.DS_Store' | wc -l` 为 24，`find . -size 0 | wc -l` 为 277。
- 来源：本次目录审计（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.99
- 状态：active

### 33) 冗余清理执行结果（P0+P1 已落地）
- 结论：P0+P1 清理已完成且收益显著：删除 `legacy_runtime/.venv`、全仓 `.DS_Store` 与两处 `stream_debug.log` 后，仓库体积约从 402M 降至 83M。
- 证据：`du -sh /Users/will/Desktop/RoadToAGI` 清理后为 `83M`；`find . -name '.DS_Store' | wc -l` 为 `0`；`/Users/will/Desktop/RoadToAGI/文案部/_archive/reset_2026-02-25/legacy_runtime/.venv` 已不存在。
- 来源：本次清理执行与复核（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.99
- 状态：active

### 34) 跨工作区最终路径策略：仅原始绝对路径纯文本
- 结论：所有新会话统一执行“原文件名 + 单反引号纯文本绝对路径”；不再输出本地 Markdown 链接，不再输出 `ASCII 安全入口`，不再输出 `%E9...` 编码路径映射。
- 证据：根目录 `AGENTS.md` 与 `agent-engineer/AGENTS.md` 已同步该强制规则；`文案部/.agent/memory` 也补充同一条结论用于覆盖旧会话习惯。
- 来源：本次全局排查与规则收口（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.99
- 状态：superseded
- 被替代说明：已收敛到条目37的“根治版单一执行模板（含禁裸文件名列表）”。

## Superseded Knowledge
- 暂无

## Reusable Patterns
- 先建立固定记忆结构，再在任务结束时沉淀高价值结论。
- 采用“索引优先、按需读取”减少上下文开销。
- 将外部方法论先拆解为“可复制机制/不可复制资产”，再转写为 Skill 的路由、流程、闸门与脚本。
- 将“人格卡”从文案偏好升级为流程依赖，先锁定边界再写作，可显著降低风格漂移。

## Last Updated
- 2026-02-26

### 35) 路径策略执行覆盖（最终）
- 结论：凡历史条目中出现别名路径、编码路径或临时入口方案，均仅作历史审计，不再作为执行策略。
- 证据：仓库级 `AGENTS.md`、`agent-engineer/AGENTS.md` 与全局 `~/.codex/AGENTS.md` 已统一为“原文件名纯文本 + 原始绝对路径纯文本”单一格式。
- 来源：本次规则收口（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.99
- 状态：superseded
- 被替代说明：已收敛到条目37的“根治版单一执行模板（含禁裸文件名列表）”。

### 36) `%E9...` 复发根因：对话可点击链接层未受仓库规则约束
- 结论：多轮修改后仍出现 `%E9...` 的直接原因不是源文件或仓库规则失效，而是“对话渲染/跳转层”仍可能对中文本地链接做 URL 编码；若编码路径不存在，就会出现空白打开。
- 证据：`assignment_A.md` 在真实路径存在且非空（3950 字节）；编码根路径 `/Users/will/Desktop/%E9%80%9A%E5%BE%80AGI%E4%B9%8B%E8%B7%AF` 已不存在；同次检查输出 `real_exists=True`、`encoded_exists=False`。
- 来源：本次用户问题复核与命令验证（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.99
- 状态：superseded
- 被替代说明：该根因已并入条目37，并补充“禁可点击本地链接 + 禁裸文件名列表”的执行模板。

### 37) 路径问题根治策略（唯一权威）
- 结论：后续交付只允许“原文件名纯文本 + 单反引号绝对路径纯文本”的两行模板；禁止任何本地 Markdown 链接、禁止裸文件名列表、禁止 ASCII/URL 编码映射兜底。
- 证据：用户于 2026-02-26 再次确认点击 `assignment_A.md` 仍为空白；同次核验显示真实文件存在而编码路径不存在（`real_exists=True`、`encoded_exists=False`）；仓库级、`agent-engineer` 与全局 `/Users/will/.codex/AGENTS.md` 均已补充“禁本地 Markdown 链接 + 禁裸文件名列表”硬规则。
- 来源：本次根治与规则收口（2026-02-26）。
- 日期：2026-02-26
- 置信度：0.99
- 状态：active
