# Agent Swarm - Content Expansion

> 基于 Agent Swarm 架构的汽车营销文案批量生成系统

---

## 📁 目录结构

```
文案部/
├── swarm_prototype.py          # 主程序（Agent Swarm 原型）
├── task_plan.md                # 任务计划（planning-with-files）
├── findings.md                 # 研究发现（planning-with-files）
├── progress.md                 # 进度日志（planning-with-files）
│
├── prompts/                    # 角色 Prompt
│   ├── 01_customer_manager.md  # 客户经理
│   ├── 02_planner.md           # 策划者
│   ├── 03_writer.md            # Writer
│   ├── 04_reviewer.md          # 审核者
│   └── 05_output_editor.md     # 输出校订者
│
├── 02-参考学习/                # 参考材料（按角色分层）
│   ├── 01-客户经理材料/
│   ├── 02-策划者材料/
│   ├── 03-Writer材料/
│   ├── 04-审核者材料/
│   └── 05-输出校订者材料/
│
├── 01-输入材料/                # 品牌方提供的资料
├── 04-产出仓库/                # 历史输出
│
├── .claude/                    # Claude 配置
│   ├── plans/                  # 分析报告
│   └── skills/                 # Skills
│
└── _archive/                   # 归档（文档、备份、旧材料）
    ├── docs/                   # 设计文档
    ├── backup/                 # 备份文件
    └── .DEV_LOG.md             # 旧开发日志
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install langgraph anthropic openpyxl
```

### 2. 设置 API Key

```bash
export ANTHROPIC_API_KEY=your_api_key
```

### 3. 运行测试

**模拟版本**（用于快速验证流程）：
```bash
python swarm_prototype.py
```

**真实 LLM 版本**（需要 API Key）：
```bash
python swarm_with_llm.py
```

### 4. 查看输出

- 模拟版本输出：`output.txt`
- LLM 版本输出：`output_llm.txt`

---

## 🏗️ 架构设计

### Agent Swarm 模式

```
@main (Orchestrator)
  ↓
客户经理 → 策划者 → Writer → 审核者 → 输出校订者
  ↓         ↓         ↓        ↓          ↓
Shared Context（Mail 机制）
```

### 核心特性

1. **职责分离**：每个角色只做一件事
2. **Shared Context**：所有角色共享状态，信息传递完整
3. **分层披露**：不同角色只看需要的材料，避免照抄
4. **质量把关**：审核者检查硬性规则，输出校订者检查 Anti-AI-style

---

## 📋 当前状态

**Phase 1: 架构设计与原型实现** ✅ COMPLETE
- 架构设计完成
- 材料重构完成
- Prompt 编写完成
- 原型代码完成
- 基础测试通过（5/5 篇）

**Phase 2: 功能完善** 🔄 IN PROGRESS
- 正在实现真实 LLM 调用
- 正在实现审核-修改循环
- 正在补充缺失材料

---

## 📝 开发进度

所有开发进度记录在 planning files 中：
- `task_plan.md` - 任务计划和阶段规划
- `findings.md` - 研究发现和洞察
- `progress.md` - 每个会话的工作日志

---

## 📚 文档

详细文档在 `_archive/docs/` 目录：
- `architecture_design.md` - 架构设计文档
- `material_migration_report.md` - 材料重构报告
- `test_plan.md` - 测试方案
- `agent_team_summary.md` - Agent Team 执行总结

---

## 🎯 下一步

1. 修复细节插入逻辑
2. 实现真实 LLM 调用
3. 实现审核-修改循环
4. 补充缺失材料
5. 实现 Excel 输出

---

_最后更新：2026-02-11_
