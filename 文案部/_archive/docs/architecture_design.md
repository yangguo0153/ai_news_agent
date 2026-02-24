# Agent Swarm 架构设计文档

> 设计者：架构师 Agent
> 日期：2026-02-11
> 版本：v1.0

---

## 一、整体架构

### 1.1 角色定义

```
@main (Orchestrator)
  ├─ 职责：调度、初始化 Shared Context、异常处理、返回结果
  ├─ 不处理业务逻辑
  └─ 使用 LangGraph 实现流程编排

业务角色（按执行顺序）：
  1. 客户经理：消化需求、与用户确认、输出 customer_brief
  2. 策划者：思考传播方向、输出 planner_brief
  3. Writer×N：并行创作内容、输出 contents
  4. 审核者：质量检查、反馈修改意见、控制循环
  5. 输出校订者：合规校验、输出 Excel
```

### 1.2 数据流图

```
用户输入
   ↓
@main (Orchestrator)
   ↓ 初始化
[Shared Context]
   ↓
客户经理 → [customer_brief] → Shared Context
   ↓
策划者 → [planner_brief] → Shared Context
   ↓
Writer×N → [contents] → Shared Context
   ↓
审核者 → [review_results] → Shared Context
   ↓ (不通过 && attempt < 3)
   └─→ Writer×N (修改)
   ↓ (通过 || attempt >= 3)
输出校订者 → [final_output] → Shared Context
   ↓
@main 返回结果
   ↓
用户输出
```

---

## 二、Shared Context 设计

### 2.1 数据结构

```python
class SharedContext(TypedDict):
    # 用户输入
    user_input: dict  # {车型, 平台, 数量, 方向}

    # 客户经理输出
    customer_brief: dict  # {需求摘要, 侧重点, 目标用户}

    # 策划者输出
    planner_brief: dict  # {传播方向, 话题切入点, 15篇分配表}

    # Writer 输出
    contents: list[dict]  # [{id, content, style, persona, attempt}]

    # 审核者输出
    review_results: list[dict]  # [{id, passed, issues, suggestions}]

    # 输出校订者输出
    final_output: str  # Excel 文件路径

    # 元数据
    metadata: dict  # {start_time, end_time, total_attempts}
```

### 2.2 Mail 机制（Context Sharing）

| 角色 | 可读取的 Context | 可写入的 Context |
|------|-----------------|-----------------|
| 客户经理 | user_input | customer_brief |
| 策划者 | user_input, customer_brief | planner_brief |
| Writer | user_input, customer_brief, planner_brief | contents |
| 审核者 | user_input, customer_brief, planner_brief, contents | review_results |
| 输出校订者 | 全部 | final_output |

**核心原则**：下游角色可以看到上游角色的所有输出，确保信息同步。

---

## 三、参考材料分层披露策略

### 3.1 目录设计

```
02-参考学习-重构版/
├── 01-客户经理材料/
│   ├── 需求消化模板.md
│   └── 常见需求类型.md
│
├── 02-策划者材料/
│   ├── 传播方向案例库.md（只有方向，无完整文案）
│   ├── 话题切入点清单.md
│   └── 用户共鸣点地图.md
│
├── 03-Writer材料/
│   ├── 结构模板库/
│   │   ├── 春节返乡-情感路线.md
│   │   ├── 春节返乡-理性对比.md
│   │   └── 家庭用车-场景展示.md
│   ├── 内容变量库/
│   │   ├── 人设角度库.md
│   │   ├── 细节描写库.md
│   │   ├── 口吻样本库.md
│   │   └── 场景切入库.md
│   └── 禁用规则/
│       ├── AI句式黑名单.md
│       └── 已用短语追踪.json
│
├── 04-审核者材料/
│   ├── 硬性规则清单.md
│   ├── 软性规则清单.md
│   └── 反例库.md
│
└── 05-输出校订者材料/
    ├── 合规性检查清单.md
    └── Anti-AI-style特征库.md
```

### 3.2 披露策略

**渐进式披露**（按角色阶段）：
- 客户经理：只看 01-客户经理材料/
- 策划者：只看 02-策划者材料/ + Shared Context
- Writer：只看 03-Writer材料/ + Shared Context
- 审核者：只看 04-审核者材料/ + Shared Context
- 输出校订者：只看 05-输出校订者材料/ + Shared Context

**随机式抽样**（Writer 阶段）：
- 每个 Writer 随机抽取 3-5 个细节描写样本
- 每个 Writer 随机抽取 2 个口吻样本
- 物理隔离，避免照抄同一样本

---

## 四、审核-修改循环控制

### 4.1 循环逻辑

```python
def review_loop(context):
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        # 审核者检查
        review_results = 审核者(context)

        # 统计通过率
        passed_count = sum(1 for r in review_results if r.passed)
        total_count = len(review_results)

        # 全部通过 → 结束循环
        if passed_count == total_count:
            context.all_passed = True
            break

        # 达到最大尝试次数 → 人工介入
        if attempt >= max_attempts:
            context.all_passed = False
            context.need_manual_review = True
            break

        # 部分不通过 → 退回修改
        failed_ids = [r.id for r in review_results if not r.passed]
        context = Writer(context, retry_ids=failed_ids, attempt=attempt+1)

    return context
```

### 4.2 人工介入触发条件

- 3 次修改仍不通过
- 审核者检测到严重问题（合规性、抄袭）
- Writer 连续失败（API 错误、超时）

---

## 五、清理清单

### 5.1 需要删除的文件/目录

```markdown
【删除】临时文件
❌ /Users/will/Desktop/通往AGI之路/文案部/progress.md
❌ /Users/will/Desktop/通往AGI之路/文案部/task_plan.md
❌ /Users/will/Desktop/通往AGI之路/文案部/findings.md

【删除】废弃目录
❌ /Users/will/Desktop/通往AGI之路/文案部/03-工作流工具/

【保留】核心目录
✅ 01-输入材料/
✅ 02-参考学习/（后续重构）
✅ 04-产出仓库/
✅ .DEV_LOG.md
✅ .claude/plans/
✅ .claude/skills/content-expansion/
```

### 5.2 备份策略

在删除前，将文件备份到：
```
backup/2026-02-11/
├── progress.md
├── task_plan.md
├── findings.md
└── 03-工作流工具/
```

---

## 六、技术实现

### 6.1 技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 流程编排 | LangGraph | 支持 StateGraph、条件边、循环 |
| LLM | Claude Opus | CLI 原型单模型 |
| 数据存储 | JSON + Markdown | 轻量级，便于调试 |
| 输出格式 | openpyxl | 生成 Excel |

### 6.2 项目结构

```
文案部/
├── swarm_prototype.py          # @main 入口
├── agents/                     # 业务角色实现
│   ├── customer_manager.py
│   ├── planner.py
│   ├── writer.py
│   ├── reviewer.py
│   └── output_editor.py
├── utils/                      # 工具函数
│   ├── context.py              # Shared Context
│   ├── materials.py            # 材料加载
│   └── random_sampler.py       # 随机抽样
├── prompts/                    # 角色 Prompt
│   ├── 01_customer_manager.md
│   ├── 02_planner.md
│   ├── 03_writer.md
│   ├── 04_reviewer.md
│   └── 05_output_editor.md
├── docs/                       # 文档
│   ├── architecture_design.md
│   ├── data_flow.md
│   └── test_plan.md
└── 02-参考学习-重构版/         # 重构后的材料
```

---

## 七、验证目标

### 7.1 功能验证

- [ ] 5 个角色能否正常协作？
- [ ] Shared Context 信息传递是否完整？
- [ ] 审核-修改循环是否收敛？
- [ ] 随机抽样是否避免照抄？

### 7.2 质量验证

- [ ] 生成内容是否符合 Brief？
- [ ] 内容是否多样化（不同细节/角度/口吻）？
- [ ] 是否避免 AI 句式（"说实话""但问题来了"）？
- [ ] 是否符合调性（温和喜庆、场景化）？

### 7.3 对比验证

| 指标 | v5.2（当前） | Swarm（新） | 目标 |
|------|-------------|------------|------|
| 同质化率 | 高 | 低 | 降低 50% |
| 照抄率 | 中 | 低 | 降低 80% |
| 审核通过率 | 60% | 80% | 提升 20% |
| 生成时间 | 15-20分钟 | 5-8分钟 | 提升 2-3倍 |

---

## 八、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 信息传递损耗 | 下游角色理解偏差 | Shared Context 完整传递 |
| 审核循环死锁 | 无限修改 | 3 次上限 + 人工介入 |
| 随机抽样重复 | 仍然照抄 | 追踪已用短语，动态禁用 |
| 单模型风格单一 | 内容同质化 | 通过人设/细节/口吻注入多样性 |

---

## 九、后续优化方向

### Phase 2（Web 阶段）
- 多模型 API 调用（GPT-4、Claude、Deepseek）
- 实时进度展示
- 人工干预点

### Phase 3（生产阶段）
- 信息抓取者角色（爬取竞品、热点）
- 用户反馈池（标注、分析、微调）
- 成本优化（弱模型做简单任务）

---

_架构师 Agent 完成_
_下一步：清理专员执行清理任务_
