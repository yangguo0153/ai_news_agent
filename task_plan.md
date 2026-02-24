# 任务计划：完善 Codex Custom Instructions（可持续记忆版）

## 目标
基于用户提供的微信文章思路与 Codex 官方机制，产出一套可落地、可迭代、可审计的 Custom Instructions 与记忆沉淀流程。

## 当前阶段
Phase 4

## 阶段拆分
### Phase 1：需求澄清与信息采集
- [x] 明确用户目标：从 Claude 迁移到 Codex，并让协作记忆可积累
- [x] 获取并解析微信文章正文（包含三层记忆、Skills、Hooks、复利引擎）
- [x] 审计当前仓库规则现状（仅有 `CLAUDE.md`，缺少 Codex 专用结构化记忆规范）
- **状态：complete**

### Phase 2：差距分析与方案设计
- [x] 梳理文章可迁移能力与不可直接迁移能力
- [x] 对齐 Codex 官方能力边界（`AGENTS.md` 分层、就近生效）
- [x] 形成 Custom Instructions v1 结构（角色、流程、记忆、验证、协作）
- [x] 明确“Skill-only vs Custom Instructions”优先级结论
- **状态：complete**

### Phase 3：落地实施
- [x] 生成/更新指令文件（优先 `AGENTS.md`，保留 `CLAUDE.md` 兼容）
- [x] 创建记忆目录与模板文件（稳定记忆、任务记忆、每日记忆）
- [x] 安装全局 `memory-compound` Skill 并补齐元数据/参考模板
- **状态：complete**

### Phase 4：验证与交付
- [x] 检查规则冲突（重复/矛盾/过度约束）
- [x] 验证关键文件均已创建并可读取
- [x] 交付最终版与后续迭代节奏
- **状态：complete**

## 关键问题
1. 你的 `Custom instructions` 要“强约束”到什么程度，才不会影响执行速度？
2. 记忆沉淀以“全自动优先”还是“人工确认后写入优先”？
3. 你希望统一在仓库内维护，还是部分放到全局 `~/.codex` 级别？

## 已确定决策
| 决策 | 理由 |
|---|---|
| 使用文件化规划（task/findings/progress） | 保障跨会话连续性，避免上下文丢失 |
| 以“分层记忆 + 渐进披露”作为核心架构 | 与文章核心思想一致，且适配 Codex 的文件读取方式 |
| 先做 v1（最小可用）再迭代 | 降低迁移成本，尽快产生收益 |
| 采用“最小 AGENTS + 全局 Skill” | AGENTS 保底稳定，Skill 提升自动化与跨项目复用 |

## 错误记录
| 错误 | 尝试次数 | 解决方式 |
|---|---:|---|
| `web.open` 无法直接抓取微信正文 | 1 | 改用 Playwright 浏览器抓取可访问页面快照 |

## 备注
- 每完成一个阶段，同步更新 `task_plan.md` 和 `progress.md`。
- 任何新增规则都要明确“触发条件 + 例外条件”，避免规则膨胀。
- 注意：新增全局 Skill 后，通常需要重启 Codex 才会稳定出现在可用 Skill 列表中。
