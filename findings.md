# Findings & Decisions

## 需求拆解
- 用户刚从 Claude Code 迁移到 Codex，希望建立长期协作机制。
- 用户目标不是一次性提示词，而是“可成长的协作系统”：随着项目推进沉淀记忆，提高后续效率。
- 用户明确希望基于给定文章进行评估，并据此启动 `Custom instructions` 完善计划。

## 研究发现
- 微信文章核心机制是“三层记忆 + 渐进式披露 + 自动触发更新（Hooks）”：
  - 第一层：结构化知识图谱（领域/主题/对象）
  - 第二层：每日事件记忆（按日期的原始记录）
  - 第三层：隐性知识（偏好、模式、经验教训）
- 文章强调“替代而非删除”记忆，即保留历史演化链路（可追溯）。
- 文章主张用 Skills 做按需加载，避免一次性塞入全部上下文。
- Codex 官方文档确认：
  - 通过 `AGENTS.md` 定义代理行为，支持分层与就近生效（根目录 + 子目录覆盖）。
  - 提示词文件应聚焦可执行规则，避免冗长、抽象、不可验证描述。
  - `AGENTS.md` 会按“全局 -> 仓库根 -> 当前子目录”顺序合并，属于稳定的 always-on 规则入口。
  - Skills 的触发依赖 `name/description` 语义匹配（隐式触发），本质是“按需触发”，不是“每次强制触发”。
- 当前项目现状：
  - 根目录仅有 `CLAUDE.md`，内容偏原则性，缺少“记忆文件结构/更新触发/验证闭环”。
  - 存在 `.agent/workflows/dev-log.md`，可作为“任务后沉淀”的衔接点。

## 技术决策
| 决策 | 理由 |
|---|---|
| 采用“规则层 + 记忆层 + 操作层”三段式 Custom Instructions | 同时覆盖行为约束、知识沉淀、执行流程 |
| 记忆文件使用纯文本可读结构（Markdown/JSON） | 易审计、易版本管理、低迁移成本 |
| 先人工确认后写入关键记忆，逐步引入自动化 | 降低误写风险，先确保质量再提速 |
| 兼容保留 `CLAUDE.md`，新增 `AGENTS.md` 作为 Codex 主入口 | 平滑迁移，不破坏既有使用习惯 |
| 若二选一：优先 Custom Instructions（AGENTS） | 稳定覆盖全部任务；Skill-only 无法保证每次都触发 |
| 最优解：最小 AGENTS + 全局记忆 Skill | AGENTS 保底一致性，Skill 提供高效流程与按需加载 |

## 已落地结果
- 已在仓库根目录新增 `AGENTS.md`（always-on 保底规则）。
- 已初始化项目记忆层：
  - `.agent/memory/INDEX.md`
  - `.agent/memory/PROFILE.md`
  - `.agent/memory/projects/default/MEMORY.md`
  - `.agent/memory/daily/2026-02-24.md`
- 已安装全局 Skill：
  - `~/.codex/skills/memory-compound/SKILL.md`
  - `~/.codex/skills/memory-compound/agents/openai.yaml`
  - `~/.codex/skills/memory-compound/references/memory_schema.md`

## 残留注意项
- 全局 Skill 新增后，通常需要重启 Codex 才会稳定生效。
- 记忆自动写回虽已具备流程定义，后续建议通过真实任务跑 1-2 次验收“触发率与写入质量”。

## 风险与对策
| 问题 | 对策 |
|---|---|
| 规则过多导致执行变慢 | 保留“硬规则最小集合”，其余下沉到模板文件 |
| 记忆污染（错误结论被固化） | 新增“证据字段 + 置信度 + 更新时间”，并要求可回滚 |
| 上下文膨胀 | 强制“索引优先、按需加载”，避免全量注入 |
| 跨项目串味 | 按项目独立 memory 空间，禁止全局混写 |

## 资源
- 微信原文链接：[蹭上150k Star的热点，从clawdbot学会了给AI加自动记忆！](https://mp.weixin.qq.com/s/Lrqf3rDPsc5Ut6OfwZYXCw?scene=1)
- Codex 指令文件官方说明：[AGENTS.md](https://openai.github.io/codex/config/)
- Codex 上下文与行为循环背景：[Unrolling the Loop](https://developers.openai.com/codex/prompting/)
- Codex AGENTS 说明：[Agents](https://developers.openai.com/codex/agents)
- Codex Skills 说明：[Skills](https://developers.openai.com/codex/skills)
- 项目现有规则文件：`/Users/will/Desktop/通往AGI之路/CLAUDE.md`

## 可视化/浏览器结论
- 已使用浏览器自动化成功打开微信链接并抓取正文结构。
- 文章中“复利引擎 5 环节循环”可直接映射为：
  - 执行任务 -> 提取事实 -> 更新分层记忆 -> 下次按需加载 -> 输出更优。
