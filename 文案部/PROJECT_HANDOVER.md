# 项目交接文档 - 汽车营销文案智能生成系统

**文档版本**: v1.0
**交接日期**: 2026-02-23
**项目历史**: 5个版本迭代
**当前状态**: 核心功能可用，内容质量待优化

---

## 目录

1. [项目概述](#1-项目概述)
2. [5个版本迭代历史](#2-5个版本迭代历史)
3. [当前架构详解](#3-当前架构详解)
4. [内容质量问题的根因分析](#4-内容质量问题的根因分析)
5. [已知Bug清单](#5-已知bug清单)
6. [交接清单](#6-交接清单)
7. [新团队接手建议](#7-新团队接手建议)
8. [关键代码位置](#8-关键代码位置)
9. [附录](#9-附录)

---

## 1. 项目概述

### 1.1 项目定位

基于 **Agent Swarm 架构** 的汽车营销文案智能批量生成系统，通过5个专业AI Agent协作，实现从需求理解到成品输出的全自动内容生产流水线。

**核心价值主张**: 让AI像资深文案团队一样工作，而非简单的文本生成器。

### 1.2 业务目标

| 目标 | 说明 |
|------|------|
| 效率提升 | 单次批量生成3-10篇差异化内容（传统方式需2-3小时） |
| 质量稳定 | 硬性规则卡点 + LLM智能审核双重保障 |
| 平台适配 | 自动适配抖音、小红书、今日头条、朋友圈等平台调性 |
| 去AI化 | 通过Anti-AI风格库和审核机制，消除机器生成痕迹 |

### 1.3 当前状态

**已完成功能**:
- ✅ LangGraph Agent流程编排（5个Agent串行+循环）
- ✅ 真实LLM调用（Deepseek API）
- ✅ 审核-修改循环（最多3次）
- ✅ Excel输出（三Sheet结构）
- ✅ Streamlit Web界面
- ✅ 并发内容生成（asyncio）

**核心问题**:
- ❌ 内容质量不稳定，初稿通过率仅20%
- ❌ 场景推演功能完全失效
- ❌ 字数控制严重失准（超标30-50%）
- ❌ 素材库随机抽样缺乏针对性

---

## 2. 5个版本迭代历史

### 版本时间线

```
v1.0 (早期) → v3.7 → v5.0 → v5.1 → v5.2 → 当前Agent Swarm
  │           │       │       │       │
  │           │       │       │       └─ 语料扩充 + 工作流修补
  │           │       │       └─ 硬编码门禁改造
  │           │       └─ Pipeline三级流水线重构
  │           └─ 反结构化强化 + 参考文档瘦身
  └─ 单Agent串行执行（问题严重）
```

### 2.1 v1.0 - 单Agent全包模式

**架构**: 单Agent串行执行全部步骤（策划→写作→审校→输出）

**核心问题**:
- 单Agent context过大（~5000字/篇），规则信号被稀释
- Writer串行生成，后续篇幅受前文模式影响（AI自我复制）
- 靠规则"提醒"模型不要重复，执行效果差

**失败原因**: 模型同时承担策划、写作、审校、查重4个角色，无法兼顾。

### 2.2 v3.7 - 反结构化强化

**改进**:
- 删除冗余文件，reference文件从907行减至533行
- 添加创作铁律检查点（STOP机制）
- 反结构化从词级替换升级为段落级禁止

**测试结果**: 同质化问题严重
- "但问题来了"句式重复：19/20篇
- "说实话"重复：8篇
- "你看"重复：6篇

**根因**: 模型缺陷（70%）+ 工作流缺陷（30%）
- 上下文稀释：Skill文档+语料库+种子库叠加后，核心流程被稀释
- 缺乏用户确认门禁

### 2.3 v5.0 - Pipeline三级流水线

**架构重构**: 从"单Agent全包"改为"Pipeline三级流水线"

```
v4.0: 主Agent串行执行全部步骤
v5.0: 主Agent编排 → Planner(分配表) → Writer×N(并行写作) → Reviewer(质检) → 输出
```

**预期效果**:
- Writer并行 → 15篇从15-20分钟降至5-8分钟
- 单篇context从~5000字降至~1200字
- 物理隔离根治同质化

**测试结果**: 流程遵循问题（跨模型复现）
- 换模型后仍复现相同偏差
- 批次违规、跳过审校、无交接

**根因**: 门禁是"描述性"的，不是"阻塞性"的
- 编排者和执行者是同一个Agent
- 控制流写在提示词层，不在代码层

### 2.4 v5.1 - 硬编码门禁改造

**改进**: 将"描述性门禁"改为"阻塞性门禁"
- 在SKILL.md中添加4个强制AskUserQuestion工具调用

**测试结果**: 整体表现不错，同质化显著改善

**残留问题**:
| 问题 | 表现 |
|------|------|
| 结尾金句相似 | 同批次多篇收尾句式雷同 |
| 数据堆砌 | 部分文章在同一段落密集罗列数据 |
| 叙事模板化 | 论证推进方式趋同 |

**根因分析**: 语料不足（50%）+ 平台特性（30%）+ 工作流缺陷（20%）

### 2.5 v5.2 - 同质化修复

**语料扩充**:
- 开头变体库：5类型 × 8变体 = 40个开头段落
- 过渡句库：4功能 × 8个 = 32个过渡句式
- 结尾变体库：5类型 × 6变体 = 30个结尾段落
- 叙事弧线模板：6结构 × 2模板 = 12个骨架模板

**文案部门反馈（严重问题）**:
| 反馈 | 问题描述 |
|------|----------|
| 方向错误 | 修复版直接讲参数，缺少春节出行场景铺垫 |
| 内容太直白 | 情感表达过于直接、沉重，缺乏文学性和画面感 |
| 内容太激进 | 语气过于犀利、负面，大过节的不够温和喜庆 |
| 卖点太轻 | 单一配置点（唱吧/LED大灯）不会为此买车 |

### 2.6 当前Agent Swarm版本

**架构**: LangGraph + 5个业务Agent

**改进**:
- 代码层控制流（LangGraph StateGraph）
- SharedContext状态管理
- 真实的审核-修改循环
- Excel格式化输出

**遗留问题**: 详见第4章

---

## 3. 当前架构详解

### 3.1 四层架构

```
┌─────────────────────────────────────────────────────────────┐
│ 表现层 (Presentation)                                        │
│ ├── Streamlit Web UI (web_ui.py)                           │
│ └── CLI 命令行 (swarm_with_llm.py::main())                 │
├─────────────────────────────────────────────────────────────┤
│ 核心层 (Core Layer) - LangGraph Agent Core                  │
│ ├── 客户经理 (需求消化)                                      │
│ ├── 策划者 (传播规划)                                        │
│ ├── Writer (并行创作)                                        │
│ ├── 审核者 (质量把关)                                        │
│ └── 输出校订者 (Excel组装)                                   │
├─────────────────────────────────────────────────────────────┤
│ 接口层 (Interface)                                          │
│ ├── Deepseek API (deepseek-chat)                           │
│ ├── tenacity (重试机制)                                     │
│ └── asyncio (并发控制)                                      │
├─────────────────────────────────────────────────────────────┤
│ 数据层 (Data Layer)                                         │
│ ├── 既定资料库 (01-输入材料/既定资料/)                      │
│ ├── 内容变量库 (02-参考学习/03-Writer材料/)                 │
│ └── 审核规则库 (02-参考学习/04-审核者材料/)                 │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 核心文件结构

```
文案部/
├── swarm_with_llm.py          # 核心代码 (1350行)
│   ├── SharedContext定义      # 第28-58行 ⚠️ 关键
│   ├── 五个Agent实现          # 第785-1265行
│   ├── 工具函数               # 第60-780行
│   └── LangGraph流程编排      # 第1272-1303行 ⚠️ 关键
├── config.py                  # 配置系统 (77行)
│   ├── PLATFORM_SPECS         # 平台规范 ⚠️ 关键
│   └── load_material()        # 单例缓存
├── web_ui.py                  # Streamlit前端 (148行)
├── 01-输入材料/               # 车型资料
│   └── 既定资料/
│       ├── CR-V.md
│       ├── HRV.md
│       ├── 思域.md
│       └── 英仕派.md
├── 02-参考学习/               # 素材库
│   ├── 01-客户经理材料/
│   ├── 02-策划者材料/
│   ├── 03-Writer材料/
│   │   ├── 结构模板库/
│   │   └── 内容变量库/        # ⚠️ 素材注入源
│   ├── 04-审核者材料/
│   └── 05-输出校订者材料/
└── 04-产出仓库/               # Excel输出
```

### 3.3 SharedContext状态流转

```python
class SharedContext(TypedDict):
    # 输入层
    user_input: Dict          # {车型, 平台, 数量, 方向}

    # 处理层
    customer_brief: Dict      # 客户经理输出
    planner_brief: Dict       # 策划者输出 (assignments分配表)
    contents: List[Dict]      # Writer输出 (多篇内容)
    review_results: List[Dict]# 审核者输出

    # 输出层
    final_output: str         # Excel文件路径

    # 控制层
    current_attempt: int      # 当前审核-修改循环次数 (1-3)
    need_manual_review: List[int]  # 需要人工介入的ID
    skip_confirmations: bool  # Web端=True，跳过确认
```

### 3.4 审核-修改循环逻辑

```python
# swarm_with_llm.py 第1185-1214行
def route_after_review(state: SharedContext) -> str:
    review_results = state["review_results"]
    current_attempt = state.get("current_attempt", 1)

    failed_items = [r for r in review_results if not r["passed"]]

    # 全部通过
    if not failed_items:
        return "输出校订者"

    # 超过3次
    if current_attempt >= 3:
        state["need_manual_review"] = [item["id"] for item in failed_items]
        return "输出校订者"

    # 返回修改
    state["current_attempt"] = current_attempt + 1
    return "Writer"
```

---

## 4. 内容质量问题的根因分析

### 4.1 核心问题诊断

| 排名 | 问题 | 严重程度 | 影响 |
|------|------|----------|------|
| 1 | 场景推演功能完全失效 | 🔴 P0 | 策划者无法动态匹配素材库 |
| 2 | 字数控制严重失准 | 🔴 P0 | 初稿通过率仅20% |
| 3 | 素材库随机抽样缺乏针对性 | 🟠 P1 | 调性不统一 |
| 4 | 审核标准过于严苛且不一致 | 🟠 P1 | 反复修改仍难通过 |
| 5 | Prompt信息过载 | 🟡 P2 | 模型难以抓住重点 |

### 4.2 问题1：场景推演功能完全失效

**证据**:
```
[策划者] 正在接收并解构宏观场景: ''...
  -> ⚠️ 场景推演失败，退回原始字符:
     name 'map_scene_to_keywords_async' is not defined
```

**影响**:
- 策划者只是简单拼接字符串，没有真正从内容变量库中匹配场景素材
- Writer无法获得精准的创作指引
- 内容与场景的关联度低

**代码位置**: `swarm_with_llm.py` 第877-885行

```python
# 策划者函数中调用了未定义的函数
try:
    enriched_scene_tags = asyncio.run(
        map_scene_to_keywords_async(direction, config.DEEPSEEK_API_KEY, config.DEEPSEEK_API_URL)
    )
except Exception as e:
    print(f"  -> ⚠️ 场景推演失败，退回原始字符: {e}")
    enriched_scene_tags = direction  # 直接退回原始字符串
```

### 4.3 问题2：字数控制严重失准

**数据**:
| 篇号 | 初稿字数 | 抖音要求 | 偏差 |
|-----|---------|---------|------|
| 2 | 401字 | 250-350字 | +51字 |
| 3 | 436字 | 250-350字 | +86字 |
| 4 | 434字 | 250-350字 | +84字 |

**根因**:
1. Writer Prompt中的字数红线描述不够强制
2. 模型对字数控制不敏感
3. 缺乏"写完后默数字数"的强制步骤

**代码位置**: `swarm_with_llm.py` 第1034行

```python
# 当前的Prompt要求
0. **【字数红线】**：必须严格控制在 **{spec['word_count']}** 的区间内！
   写完后在心里默数一遍字数，坚决不准超出上限或低于下限！
```

### 4.4 问题3：素材库随机抽样缺乏针对性

**当前实现** (随机抽样):
```python
# swarm_with_llm.py 第985-991行
selected_details = random_sample_details(detail_samples, k=3)
persona_opening = random.sample(persona_samples.get("开场切入", [""]), min(2, ...))
persona_pain = random.sample(persona_samples.get("痛点描述", [""]), min(2, ...))
scene_samples = load_scene_samples(customer_brief['方向'])
```

**问题**:
- 素材是随机抽取的，与人设/卖点的匹配度全凭运气
- 宝妈人设可能抽到"职场精英"风格的素材
- 缺乏素材与目标匹配的算法

### 4.5 问题4：审核标准过于严苛且不一致

**审核反馈矛盾示例**:
- 篇1：6分，"有轻微套路化痕迹" + "数据支撑尚可但可更扎实"
- 修改后：篇1仍然6分，"数据支撑不足" + "低层次情绪词汇"

**根因**:
- LLM审核温度过低（0.1），导致过度敏感
- 审核标准主观性强
- 不同审核批次标准不一致

**代码位置**: `swarm_with_llm.py` 第638-639行

```python
payload = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.1,  # 过低，导致过度敏感
    "max_tokens": 512
}
```

### 4.6 问题5：Prompt信息过载

**Writer Prompt现状**:
- 字数：约2000字
- 包含：车型资料 + 平台规范 + 人设分配 + 素材注入 + Few-Shot + 5大强制规则

**影响**:
- 模型难以抓住重点
- 容易遗漏关键约束（如字数、参数要求）

---

## 5. 已知Bug清单

### 5.1 致命Bug（P0）

| Bug | 描述 | 位置 | 修复建议 |
|-----|------|------|----------|
| 场景推演函数未定义 | `map_scene_to_keywords_async` 函数被调用但未定义 | swarm_with_llm.py:879 | 实现该函数或移除调用 |
| API密钥硬编码 | config.py中有默认API Key | config.py:13 | 强制从环境变量读取 |

### 5.2 严重Bug（P1）

| Bug | 描述 | 位置 | 修复建议 |
|-----|------|------|----------|
| 字数控制失效 | 初稿字数普遍超标30-50% | Writer Prompt | 添加强制字数检查步骤 |
| 素材随机抽样 | 素材与人设/卖点匹配度低 | swarm_with_llm.py:985 | 实现定向匹配算法 |
| 审核标准过严 | 温度0.1导致过度敏感 | swarm_with_llm.py:639 | 调整为0.3-0.5 |
| 审核反馈矛盾 | 同一篇修改后仍不通过 | 审核逻辑 | 校准审核标准 |

### 5.3 一般Bug（P2）

| Bug | 描述 | 位置 | 修复建议 |
|-----|------|------|----------|
| Excel依赖同步IO | generate_excel_output使用同步写入 | swarm_with_llm.py:379 | 使用线程池 |
| 缺少输入验证 | user_input字段未做合法性校验 | web_ui.py | 添加Pydantic验证 |
| 状态无持久化 | SharedContext仅在内存中 | 全局 | 添加Redis持久化 |
| 单点故障 | 仅依赖Deepseek一个API | 全局 | 添加备用LLM |
| 内容无去重 | 并发创作可能产生相似内容 | Writer | 添加相似度检测 |

### 5.4 技术债务（PROJECT_ARCHITECTURE.md中提及）

| Bug编号 | 问题 | 当前状态 |
|--------|------|----------|
| Bug-1 | 配置与业务逻辑耦合 | 部分修复（API已抽离） |
| Bug-2 | 并发模式下的高频文件I/O | ✅ 已修复（单例缓存） |
| Bug-3 | API无异常保护断路器 | 部分修复（有重试，无信号量） |
| Bug-4 | 场景推理未形成真正映射 | ❌ 未修复（函数未定义） |

---

## 6. 交接清单

### 6.1 项目文件清单

**核心代码文件**:
- [x] `swarm_with_llm.py` - 主程序 (1350行)
- [x] `config.py` - 配置系统
- [x] `web_ui.py` - Streamlit前端

**文档文件**:
- [x] `README.md` - 项目概况
- [x] `PROJECT_ARCHITECTURE.md` - 架构文档与Bug检测
- [x] `IMPLEMENTATION_SUMMARY.md` - 实施总结
- [x] `项目总览.md` - 完整项目文档
- [x] `PROJECT_HANDOVER.md` - 本交接文档

**素材库**:
- [x] `01-输入材料/既定资料/` - 车型知识库 (4款车型)
- [x] `02-参考学习/` - 6大类素材库
  - [x] 口吻样本库 (4种人设)
  - [x] 场景切入库 (5种场景)
  - [x] 细节描写库 (69条样本)
  - [x] 爆款参考库
  - [x] 硬性规则清单
  - [x] Anti-AI-style特征库

### 6.2 依赖清单

```bash
# requirements.txt
langgraph
anthropic
openpyxl
tenacity
aiohttp
streamlit
pandas
PyPDF2
python-docx
dotenv
```

### 6.3 环境变量

```bash
# .env 文件
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
```

### 6.4 运行方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置环境变量
export DEEPSEEK_API_KEY=your_api_key

# 3. 运行Web界面
streamlit run web_ui.py

# 4. 或运行命令行版本
python swarm_with_llm.py
```

---

## 7. 新团队接手建议

### 7.1 立即行动（第一周）

**优先级P0 - 修复致命Bug**:
1. **修复场景推演函数**
   - 实现 `map_scene_to_keywords_async` 函数
   - 或移除调用，使用简单的关键词匹配

2. **强化字数控制**
   - 在Prompt中添加"写完后默数字数"的强制步骤
   - 添加字数检查函数，超标时自动截断或重写

3. **移除硬编码API Key**
   - 从config.py中移除默认值
   - 强制从环境变量读取

### 7.2 短期优化（第二周）

**优先级P1 - 提升内容质量**:
4. **素材精准匹配**
   - 根据人设+卖点+场景三要素定向选择素材
   - 实现简单的TF-IDF或Embedding匹配

5. **校准审核标准**
   - 将LLM审核温度从0.1调整到0.3
   - 统一审核标准，减少主观性

6. **Prompt重构**
   - 拆分为"系统指令+角色设定+创作任务+格式要求"四层
   - 减少单Prompt信息量

### 7.3 中期优化（第一个月）

7. **多模型支持**
   - 添加Claude、GPT-4等备用模型
   - 实现模型failover机制

8. **状态持久化**
   - 添加Redis或SQLite持久化
   - 支持断点恢复

9. **内容去重**
   - 添加相似度检测
   - 实现多样性约束

### 7.4 架构升级建议

**如果当前架构无法满足质量要求，考虑以下升级**:

| 升级方向 | 说明 | 复杂度 |
|----------|------|--------|
| RAG增强 | 使用向量数据库存储素材，实现真正的语义匹配 | 中 |
| 微调模型 | 使用领域数据微调小型模型 | 高 |
| 人工反馈闭环 | 添加用户反馈收集和模型迭代 | 中 |
| A/B测试框架 | 对比不同Prompt/模型的效果 | 低 |

---

## 8. 关键代码位置

### 8.1 绝对不能修改的区域

```python
# ⚠️ 危险区域 1: SharedContext 定义
# 位置: swarm_with_llm.py 第28-58行
class SharedContext(TypedDict):
    # 修改字段名会导致整个状态流转失败

# ⚠️ 危险区域 2: LangGraph 流程编排
# 位置: swarm_with_llm.py 第1272-1303行
def create_swarm():
    # 修改顺序会破坏依赖关系

# ⚠️ 危险区域 3: 审核-修改循环路由
# 位置: swarm_with_llm.py 第1185-1214行
def route_after_review(state: SharedContext) -> str:
    # 这个阈值不能随意修改
    if current_attempt >= 3:

# ⚠️ 危险区域 4: 平台规格配置
# 位置: config.py 第20-44行
PLATFORM_SPECS = {
    # 修改会影响审核逻辑
}
```

### 8.2 需要优化的代码区域

```python
# 🔧 优化区域 1: 场景推演
# 位置: swarm_with_llm.py 第877-885行
# 当前: 调用未定义的函数
# 需要: 实现真正的场景匹配

# 🔧 优化区域 2: 素材抽样
# 位置: swarm_with_llm.py 第985-991行
# 当前: random.sample 随机抽样
# 需要: 基于人设+卖点的定向匹配

# 🔧 优化区域 3: 审核温度
# 位置: swarm_with_llm.py 第639行
# 当前: temperature=0.1
# 建议: temperature=0.3
```

---

## 9. 附录

### 9.1 历史文档存档位置

```
_archive/
├── docs/                       # 设计文档
│   ├── architecture_design.md
│   ├── agent_team_summary.md
│   └── material_migration_report.md
├── old-materials/              # 旧版素材
│   └── 02-参考学习/
├── old-claude-config/          # 旧版配置
│   └── skills/content-expansion/
└── .DEV_LOG.md                 # 开发日志
```

### 9.2 关键业务规则

**内容创作黄金法则**:
```
【开头】春节场景感性切入（30-50字）
【中段】以前vs现在的对比（80-120字）
【转折】为什么选CR-V（大维度价值）（80-120字）
【结尾】情感升华+祝福（30-50字）
```

**参数使用原则**:
- 参数是支撑，不是主角
- 必须包含1-2个宏观卖点 + 2-3个具体物理参数
- 轻量配置不单独成篇

**禁用词清单**:
```python
['说实话', '但问题来了', '你看', '首先', '其次', '方面', '不得不说']
```

### 9.3 联系方式

**前任负责人**: 用户带过5个版本，发现内容质量是核心瓶颈
**当前状态**: 准备切换API接口，需要新团队接手优化

---

**文档结束**

_祝新团队顺利接手，早日解决内容质量问题！_
