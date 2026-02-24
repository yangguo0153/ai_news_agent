# Task Plan: v5.2 — 语料扩充完成，准备验证

## Goal

v5.1: 在 SKILL.md 中将所有"描述性门禁"改为"阻塞性门禁"
v5.2: 引入 OpenClaw 语料解决同质化问题，验证整个 Pipeline

## Current Phase

Phase 5: 验证阶段（语料已就位 ✅）

## Phases

### Phase 1: 诊断 — 定位所有"可跳过"节点

- [x] 列出 SKILL.md 中所有门禁点
- [x] 对照复盘报告确认每个被跳过的节点
- [x] 将诊断结果写入 findings.md
- **Status:** complete

### Phase 2: 设计 — 硬编码断点方案

- [x] 为每个门禁点设计 AskUserQuestion 调用指令
- [x] 设计 ⛔ 执行铁律（4 条禁令）
- [x] 设计伪代码批次循环
- **Status:** complete

### Phase 3: 实施 — 修改 SKILL.md

- [x] 加入 ⛔ 执行铁律段落
- [x] Step 3/4/5/6 加入 🚫 门禁
- [x] 删除冗余（风格映射表、人机共驾）
- **Status:** complete

### Phase 4: 更新开发日志

- [x] .DEV_LOG.md 记录 v5.0 测试结果 + v5.1 改动
- **Status:** complete

### Phase 5: 验证阶段

- [x] v5.1 硬编码门禁实施完成
- [x] v5.2 OpenClaw 语料已就位（6个文件已复制）
- [ ] 工作流验证（5篇头条冒烟测试）
- [ ] 端到端验证（20篇压力测试）
- **Status:** in_progress

## Key Questions

1. 是否需要同时修改 Writer/Reviewer/Planner 的 prompt 模板？（初步判断：不需要，问题在编排层不在执行层）
2. 批次大小是否仍为 3 篇/批？（沿用现有规定）
3. AskUserQuestion 的选项如何设计才能让用户操作最简？

## Decisions Made

| Decision                           | Rationale                                                 |
| ---------------------------------- | --------------------------------------------------------- |
| 只改 SKILL.md，不改子 Agent prompt | 问题出在编排层（主 Agent），不在执行层（Writer/Reviewer） |
| 用 AskUserQuestion 作为物理门禁    | 这是 Claude Code 环境下唯一的阻塞式交互工具               |
| 不引入脚本（方案 A 优先）          | 最小改动原则，验证失败再升级方案 B                        |

## Errors Encountered

| Error  | Attempt | Resolution |
| ------ | ------- | ---------- |
| (暂无) | —       | —          |

## Notes

- 本次改动范围：SKILL.md + .DEV_LOG.md，共 2 个文件
- 不改动任何 references/ 下的子 Agent prompt 文件
- 方案 A 验证标准：用最弱模型测试 5 篇头条，观察是否每个门禁都被执行
