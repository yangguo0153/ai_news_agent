# Default Project Memory

## Active Knowledge
### 1) 仓库阶段
- 结论：当前仓库已进入“有文档沉淀 + 可运行脚本”的中后期阶段，不是空白起步状态。
- 证据：根目录存在 `PROJECT_HANDOVER.md`、`IMPLEMENTATION_SUMMARY.md`、`PROJECT_ARCHITECTURE.md` 与主程序文件。
- 来源：仓库目录结构检查（`ls -la`）。
- 日期：2026-02-25
- 置信度：0.93
- 状态：active

### 2) 版本状态
- 结论：本地 `main` 分支领先远端 1 个提交，说明存在尚未同步的进展。
- 证据：`git status --short --branch` 输出 `## main...origin/main [ahead 1]`。
- 来源：Git 状态检查命令输出。
- 日期：2026-02-25
- 置信度：0.98
- 状态：active

### 3) 文档一致性
- 结论：项目文档存在“状态不同步”，README 进度描述落后于交接文档与总览文档。
- 证据：`README.md` 标注 Phase 2 进行中且最后更新 2026-02-11；`PROJECT_HANDOVER.md`/`项目总览.md` 更新时间为 2026-02-23，并给出更完整架构与风险结论。
- 来源：文档交叉读取（README、PROJECT_HANDOVER、项目总览）。
- 日期：2026-02-25
- 置信度：0.97
- 状态：active

### 4) 产出活跃度
- 结论：系统近期仍有产出活动，产出仓库共有 24 份 Excel 结果，最近产出时间为 2026-02-25 13:36:10 +0800。
- 证据：`find 04-产出仓库 -type f | wc -l` 返回 24，最新文件时间戳经 `date -r` 转换为 2026-02-25 13:36:10 +0800。
- 来源：命令输出（find/wc/stat/date）。
- 日期：2026-02-25
- 置信度：0.96
- 状态：active

### 5) 当前主阻塞
- 结论：核心阻塞从“功能缺失”转为“质量稳定性与策略匹配”，包括场景推演、字数控制、素材匹配精准度。
- 证据：`PROJECT_HANDOVER.md` 第 4 章集中列出内容质量根因；`IMPLEMENTATION_SUMMARY.md` 仍保留 Phase 3 建议任务。
- 来源：项目交接文档与实施总结文档。
- 日期：2026-02-25
- 置信度：0.94
- 状态：active

## Reusable Patterns
- 对进度盘点类任务，优先使用“Git 状态 + 结构化文档 + 最近提交”三段证据链，避免只看单一指标。
- 若工作目录是仓库子目录，先确认 `git rev-parse --show-toplevel`，再判断提交与文件范围，避免误读“ahead/behind”影响面。

### 6) 阶段策略：先重评再开发
- 结论：项目已进入阶段暂停（pause），短期内不再以“持续跑批 + 循环改写”作为主路径，优先做业务模型与质量目标重评。
- 证据：用户明确给出 `status=pause`，当前问题为 `quality_bottleneck`，并列出“同质化、质量停滞”。
- 来源：用户输入 JSON（2026-02-25 当前会话）。
- 日期：2026-02-25
- 适用范围：文案部项目下一阶段决策（需求、架构、评估口径）。
- 置信度：1.0
- 标签：#pause #重评 #质量瓶颈
- 状态：active

### 7) 产能约束已明确为硬指标
- 结论：文案部目标产能为“抖音脚本 150/人/日 + 头条文章 100/人/日”，后续方案必须先验证该指标下的人机分工与质量门槛，而非继续增加系统复杂度。
- 证据：用户提供 daily_output_per_person 硬指标，并明确“复杂度误判、初始策略缺陷”。
- 来源：用户输入 JSON（2026-02-25 当前会话）。
- 日期：2026-02-25
- 适用范围：系统目标定义、验收标准、流程拆分。
- 置信度：0.99
- 标签：#产能 #目标约束 #人机协同
- 状态：active

### 8) 重评决策稿已形成统一执行蓝本
- 结论：项目已形成阶段性“重评一页纸决策稿”，后续应按该稿执行“先质量治理、再产能放量、30 天 Go/No-Go”。
- 证据：决策稿明确了四项即时决策、三类 KPI、四周里程碑、Go/No-Go 判定与管理层待确认项。
- 来源：`/Users/will/Desktop/RoadToAGI/文案部/RE_EVAL_ONE_PAGER_2026-02-25.md`。
- 日期：2026-02-25
- 适用范围：暂停后的阶段管理、跨团队对齐、资源投入决策。
- 置信度：0.99
- 标签：#重评 #决策稿 #go-no-go #阶段治理
- 状态：active

### 9) 项目状态已归零重启（2026-02-25）
- 结论：项目执行面已清零，旧运行代码与测试已整体下线并归档，当前阶段以“重启调研”替代“继续开发”。
- 证据：`_archive/reset_2026-02-25/legacy_runtime/` 包含原执行代码与测试；工作面根目录已无活动 `.py` 文件。
- 来源：文件迁移结果 + `find . -path './_archive' -prune -o -type f -name '*.py' -print`。
- 日期：2026-02-25
- 适用范围：文案部项目当前阶段管理与后续协作入口。
- 置信度：0.99
- 标签：#归零 #重启 #调研优先
- 状态：active

### 10) 新工作入口已固定为“00-重启调研”
- 结论：新阶段所有工作从 `00-重启调研/` 启动，且“阶段性成功 + 决策稿”已作为输入资料固化。
- 证据：目录中已存在 `00-重启总纲.md`、`01-阶段性成功与决策资料.md`、`02-新一轮调研计划.md`、`03-调研启动发现_v0.md` 与输入资料副本。
- 来源：`find 00-重启调研 -maxdepth 3 -type f`。
- 日期：2026-02-25
- 适用范围：重启调研阶段的执行路径、资料查阅顺序、交付口径。
- 置信度：0.99
- 标签：#调研入口 #资料固化 #阶段切换
- 状态：active

## Superseded Knowledge
- 结论：旧“仓库阶段为中后期可运行脚本”判断已被“归零重启”覆盖。
- superseded对象：`Active Knowledge -> 1) 仓库阶段`
- 新结论：见 `Active Knowledge -> 9) 项目状态已归零重启（2026-02-25）`
- 日期：2026-02-25
- 原因：用户明确要求归零并删除大量旧代码，当前执行面已转为调研。
- 状态：superseded

### 11) 三源调研输入已完成可用性盘点
- 结论：重启阶段三源输入（风格语料、抓取语料、及格文稿池）均可直接用于调研建模，且及格文稿池具备规模化分析价值（1557 条脚本）。
- 证据：三源盘点结果：`/Users/will/Desktop/语料生产任务` 与 `/Users/will/Desktop/本田语料库完整版` 均为 6 个 Markdown 文件；Excel 解析得到 43 张表、6193 行、1557 条脚本。
- 来源：`00-重启调研/04-三源资料盘点_2026-02-25.md`。
- 日期：2026-02-25
- 适用范围：重启调研阶段的数据输入定义与样本池基线。
- 置信度：0.99
- 标签：#三源调研 #输入盘点 #及格语料池
- 状态：active

### 12) 调研执行位策略：当前用 Main，实验期再开 worktree
- 结论：本轮以 Main 承载调研文档与规则设计，暂不新建 worktree；当进入并行代码实验线时再启用 worktree 隔离。
- 证据：当前任务不涉及高风险并行开发，且主工作区已归零重启；任务包已定义 worktree 触发条件。
- 来源：`00-重启调研/05-三源语料调研任务包_v1.md`。
- 日期：2026-02-25
- 适用范围：重启前半程协作方式与分支/目录管理。
- 置信度：0.95
- 标签：#main-first #worktree-trigger #协作策略
- 状态：active

### 13) 及格语料底线画像已完成（300样本）
- 结论：及格语料的主要瓶颈不是信息缺失，而是“叙事弧线与句式模板化”；同质化可通过门禁阈值直接治理。
- 证据：300 样本统计显示 `对比评测 33.3% + 促销权益收口 30.3%`，禁用句型命中率 `13.3%`（`不是…而是…` 37 次）。
- 来源：`/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/06-及格语料底线画像_v1.md`。
- 日期：2026-02-25
- 适用范围：门禁规则设计、批次质量评估、同质化治理优先级。
- 置信度：0.97
- 标签：#底线画像 #同质化 #门禁阈值
- 状态：active

### 14) Excel 解析技术路线确认（openpyxl 失败 -> XML 解包）
- 结论：当前及格文稿池 Excel 应使用“XML 解包 + 字段映射”作为默认解析方案，避免 openpyxl 样式兼容问题导致任务中断。
- 证据：openpyxl 报错 `TypeError: Fill() takes no arguments`；XML 解析可稳定读取 43 个 sheet、1557 条脚本。
- 来源：本会话执行日志与 `06-附录_300样本标注_v1.csv` 产出结果。
- 日期：2026-02-25
- 适用范围：后续抽样、质检、统计脚本的数据层实现。
- 置信度：0.99
- 标签：#excel解析 #技术路线 #稳定性
- 状态：active

### 15) 风格映射缺口已量化（任务B完成）
- 结论：过审语料的核心失衡是“风格配额失衡”，S2 过量、S3/S5 缺失，导致同质化在结构层面反复出现。
- 证据：N=300 映射结果显示 S2=72.0%，S3=0.3%，S5=0.3%，且 E 模板未匹配率 91.7%、T 模板严格命中率 0.0%。
- 来源：`/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/07-风格映射与缺口报告_v1.md`。
- 日期：2026-02-25
- 适用范围：风格治理策略、门禁规则配置、后续试运行验收。
- 置信度：0.95
- 标签：#风格映射 #缺口分析 #同质化
- 状态：active

### 16) 下一阶段优先级应为“门禁+配额”而非放量
- 结论：在进入小规模试运行前，必须先落地风格配额门禁（S/H/T/E/L），否则继续跑批会扩大低质量同质输出。
- 证据：报告 Top 10 策略前半部分聚焦 S3/S5 补位、S2 压降、Lx 促销收口压降、E 模板补齐。
- 来源：`07-风格映射与缺口报告_v1.md` 第四章与第五章。
- 日期：2026-02-25
- 适用范围：任务C（阻塞性门禁规则）与任务D（试运行方案）前置条件。
- 置信度：0.94
- 标签：#优先级 #门禁规则 #配额治理
- 状态：active

### 17) 阻塞性门禁规则已落地（任务C完成）
- 结论：项目已建立可执行的 `G0-G4` 阻塞性门禁，替代原“描述性规则”，并把自动改写改为“最多一次+失败分流”。
- 证据：规则文档定义了硬门禁、软门禁、批次阈值、熔断、人工接管；配置文件固化阈值与正则模式。
- 来源：
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/08-阻塞性门禁规则_v1.md`
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/08-门禁阈值配置_v1.yaml`
- 日期：2026-02-25
- 适用范围：任务C后所有批量生成质检、失败分流、试运行验收。
- 置信度：0.97
- 标签：#阻塞性门禁 #熔断 #失败分流
- 状态：active

### 18) 单一配置源策略已明确
- 结论：生成/审核/修订必须共享同一阈值配置源，禁止多套规则并存导致质量判定漂移。
- 证据：规则文档第九章明确“门禁只认单一配置源”，配置文件 `08-门禁阈值配置_v1.yaml` 已创建。
- 来源：`08-阻塞性门禁规则_v1.md`、`08-门禁阈值配置_v1.yaml`。
- 日期：2026-02-25
- 适用范围：后续实现门禁脚本、试运行看板、回归对比。
- 置信度：0.98
- 标签：#single-source-of-truth #阈值治理 #防漂移
- 状态：active

### 19) 已形成外部策略评估输入稿（ChatGPT 5.2 Pro）
- 结论：项目已形成可外发的“整体回顾文档”，可用于外部模型在同一证据基线下评估后续开发策略。
- 证据：文档包含项目目标、硬约束、A/B/C策略对比、当前阻塞、待咨询问题与输出口径。
- 来源：`/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/10-项目整体回顾_供外部策略评估_2026-02-26.md`。
- 日期：2026-02-26
- 适用范围：外部专家模型评估、管理层对齐、阶段策略复核。
- 置信度：0.98
- 标签：#外部评估 #策略复盘 #对齐文档
- 状态：active

### 20) 当前推荐策略仍为 C（双轨混合）
- 结论：在现有证据下，优先“业务小样验证 + 最小门禁执行器并行”比纯工程优先或纯运营优先更稳妥。
- 证据：A/B/C 对比中，A 返工风险高、B 技术积累慢，C 兼顾验证速度与工程沉淀。
- 来源：`10-项目整体回顾_供外部策略评估_2026-02-26.md` 第9-10章。
- 日期：2026-02-26
- 适用范围：任务D启动前的路线决策、资源分配与节奏控制。
- 置信度：0.95
- 标签：#双轨混合 #策略方向 #governance
- 状态：active

### 21) 5.2 Pro 建议已完成架构级落地拆解
- 结论：已将外部建议从“方向描述”转为“执行级框架”，明确了保留项、必须调整项、暂缓项，避免再次陷入大而全开发。
- 证据：新文档给出 vNext 模块边界、数据合同、G0-G4 门禁执行原则、14天双轨计划与 Go/No-Go 指标。
- 来源：`/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/11-架构拆解与执行计划_基于5.2pro建议_2026-02-26.md`。
- 日期：2026-02-26
- 适用范围：任务D（人机协同试运行）与门禁执行器最小实现阶段。
- 置信度：0.97
- 标签：#架构拆解 #执行计划 #g0-g4 #go-no-go
- 状态：active

### 22) 30天评估口径已具体化为6项量化指标
- 结论：阶段评估不再用主观“感觉变好”，而是绑定通过率、同质化命中、人工改动时长、配额达标与熔断频次等量化阈值。
- 证据：新增执行计划文档第6章定义 6 项 Go/No-Go 指标与否决条件（连续两周不达标）。
- 来源：`11-架构拆解与执行计划_基于5.2pro建议_2026-02-26.md` 第6章。
- 日期：2026-02-26
- 适用范围：30天资源再分配决策与阶段复盘。
- 置信度：0.94
- 标签：#指标治理 #go-no-go #阶段决策
- 状态：active

### 23) 路径交付策略已切换为“原始绝对路径纯文本”
- 结论：本项目后续交付路径统一为“原文件名 + 单反引号包裹的原始绝对路径”；禁止输出本地 Markdown 链接、`ASCII 安全入口`、`/tmp/agi-road-links/*`、`/Users/will/Desktop/agi-road/*` 与 `%E9...` 编码映射路径。
- 证据：仓库级与 `agent-engineer` 规则已同步为同一策略；历史 ASCII 入口方案已被用户明确拒绝并下线。
- 来源：本次用户约束收口（2026-02-26）。
- 日期：2026-02-26
- 适用范围：文案部全部新会话与交付汇报。
- 置信度：0.99
- 标签：#path-policy #plain-path #no-ascii #no-urlencode
- 状态：superseded
- 被替代说明：已收敛到条目43的“根治版单一执行模板（含禁裸文件名列表）”。

### 24) D1 已建立 vNext 最小执行规格（workflow_spec）
- 结论：项目已具备可执行的工作流合同基线，后续 D2-D4 可直接基于该规格实现 CLI 门禁执行器与 harness。
- 证据：新增 `vnext-mvp/workflow_spec.yaml`，内容覆盖节点顺序、状态机、G0-G4 输入输出、rewrite_policy、failure_router、metrics 与 go_no_go 阈值。
- 来源：`/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/workflow_spec.yaml`。
- 日期：2026-02-26
- 适用范围：重启阶段技术实现入口（D2-D4）与评估口径统一。
- 置信度：0.98
- 标签：#workflow-spec #gates #state-machine #mvp14d
- 状态：active

### 25) D1 验证方式固定为“语法校验 + 关键字段探针”
- 结论：规格文件落地后必须执行两类快速校验：YAML 语法校验与关键字段存在性探针，避免后续接线时才暴露结构问题。
- 证据：本次执行了 `python3 + yaml.safe_load` 和 `rg` 关键段落检查，确认 `gates/rewrite_policy/metrics/go_no_go` 均存在。
- 来源：本会话命令输出（2026-02-26）。
- 日期：2026-02-26
- 适用范围：后续 `workflow_spec.yaml`、`gate_config.yaml`、`harness_config.yaml` 变更提交前。
- 置信度：0.97
- 标签：#validation #yaml #quality-gate
- 状态：active

### 26) 路径策略执行覆盖（最终）
- 结论：凡历史条目中出现别名路径、编码路径或临时入口方案，均仅作历史审计，不再用于文案部新对话交付。
- 证据：文案部、仓库级与全局规则已统一为“原文件名纯文本 + 原始绝对路径纯文本”单一格式。
- 来源：本次规则收口（2026-02-26）。
- 日期：2026-02-26
- 适用范围：文案部全部新会话与交付汇报。
- 置信度：0.99
- 标签：#path-policy #final-override
- 状态：superseded
- 被替代说明：已收敛到条目43的“根治版单一执行模板（含禁裸文件名列表）”。

### 27) D2 已建立 vNext 门禁统一配置源（gate_config）
- 结论：项目已从“规则文档 + 分散阈值”升级为“可执行门禁配置”，D2 统一收敛到 `vnext-mvp/gate_config.yaml`。
- 证据：配置包含路由、G0-G4、一次改写策略、失败码字典与审计字段，且 `workflow_spec.references.gate_config_yaml` 已指向该文件。
- 来源：
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/gate_config.yaml`
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/workflow_spec.yaml`
- 日期：2026-02-26
- 适用范围：D3 CLI runner、D4 harness 与后续门禁参数回放。
- 置信度：0.98
- 标签：#gate-config #single-source-of-truth #g0-g4
- 状态：active

### 28) 环境路径基线已修正为 RoadToAGI
- 结论：当前仓库真实根路径为 `/Users/will/Desktop/RoadToAGI/文案部`，旧路径 `/Users/will/Desktop/RoadToAGI/Copywriting` 在本机不存在；后续命令与文档引用必须统一到新路径。
- 证据：旧路径 `ls` 失败（No such file or directory），`find /Users/will/Desktop -name 文案部` 返回 `RoadToAGI/文案部`。
- 来源：本会话命令输出（2026-02-26）。
- 日期：2026-02-26
- 适用范围：后续全部自动化命令、文件写入、文档绝对路径引用。
- 置信度：0.99
- 标签：#environment #path-baseline #execution-stability
- 状态：active

### 29) D3 最小门禁执行器已可运行（G0->G1->G2->G4）
- 结论：重启阶段已从“纯规格文档”进入“可执行门禁验证”，D3 runner 可直接读取 D1/D2 配置并产出结构化分流结果。
- 证据：`d3_gate_runner.py` 以 `workflow_spec.yaml + gate_config.yaml` 驱动，输出 `items[]/batch_g4/summary`。
- 来源：`/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/d3_gate_runner.py`。
- 日期：2026-02-26
- 适用范围：D4 harness 接线与后续门禁回归测试。
- 置信度：0.98
- 标签：#d3 #gate-runner #mvp
- 状态：active

### 30) 门禁配置存在“非正则字面量模式”风险，执行器必须做兼容
- 结论：`gate_config.yaml` 中存在 `(字幕` 这类非合法正则的字面量模式；执行器若直接 `re.search` 会崩溃，必须支持“正则失败回退字面量匹配”。
- 证据：运行时报错 `re.error: missing ), unterminated subpattern`，修复后样例可正常执行。
- 来源：D3 运行日志 + `d3_gate_runner.py` 中 `contains_any_pattern` 兼容逻辑。
- 日期：2026-02-26
- 适用范围：所有读取 `supplemental_patterns/banned_patterns` 的执行器实现。
- 置信度：0.99
- 标签：#regex #compatibility #stability
- 状态：active

### 31) G4 连续失败码统计需处理 PASS 项空失败码边界
- 结论：批次统计逻辑不能假设每条都有失败码；若 `fail_codes=[]`，必须安全降级为 `None`，否则会触发索引越界。
- 证据：错误日志 `IndexError: list index out of range`，修复后 smoke 样例得到 `PASS=2, REWRITE_ONCE=1, breaker=false`。
- 来源：D3 运行日志 + `d3_gate_runner.py` 中 `longest_same_code_run` 修复。
- 日期：2026-02-26
- 适用范围：D4 harness 与后续批次统计模块。
- 置信度：0.98
- 标签：#g4 #edge-case #batch-metrics
- 状态：active

### 32) D4 评估Harness已落地，可从D3结果自动出指标与判定
- 结论：项目已形成“执行器 -> 评估器”最小闭环，D4 harness 可聚合多份 D3 报告并输出阈值对比与决策信号。
- 证据：`d4_eval_harness.py` 输出 `d4_eval_report.json/md`，包含 `metrics`、`threshold_evaluation`、`decision`。
- 来源：
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/d4_eval_harness.py`
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/d4_eval_report.json`
- 日期：2026-02-26
- 适用范围：D4-D5 试运行评估、周报指标看板、Go/No-Go 会议输入。
- 置信度：0.98
- 标签：#d4 #eval-harness #go-no-go
- 状态：active

### 33) 当前决策信号解释：NO_GO_CANDIDATE仅代表单窗口预警
- 结论：`NO_GO_CANDIDATE` 不能直接等同最终 No-Go；需按规则做连续窗口验证（至少两周/多窗口）再做资源决策。
- 证据：`decision.note` 明确声明 `single-window result only`，并引用 workflow_spec 的连续窗口条件。
- 来源：
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/d4_eval_report.json`
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/workflow_spec.yaml`
- 日期：2026-02-26
- 适用范围：管理层汇报口径、阶段决策节奏控制。
- 置信度：0.97
- 标签：#decision-signal #windowing #governance
- 状态：active

### 34) D4缺失指标策略：显式MISSING，禁止填充伪值
- 结论：对于 `avg_manual_edit_minutes`、`style_quota_hit_rate` 等无数据项，当前策略为 `MISSING + skip`，避免人为补值污染判定。
- 证据：`harness_config.policy.missing_metric_policy=skip`，报告中对应指标为 `MISSING`。
- 来源：
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/harness_config.yaml`
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/d4_eval_report.json`
- 日期：2026-02-26
- 适用范围：D4后续数据接入（人工时长、风格配额）前的评估策略。
- 置信度：0.98
- 标签：#missing-metrics #evidence-first #no-fake-data
- 状态：active


### 35) D5 双轨口径已落地并完成首轮验收
- 结论：评估体系已实现“旧流程只技术回放、新流程才进质量基线”的硬隔离，避免 legacy 数据污染 Go/No-Go 结论。
- 证据：质量主报告 `report_scope=quality_baseline`，并排除 23 份 legacy 报告；replay 报告仅统计 legacy 数据。
- 来源：
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/runs/eval/d4_eval_report_quality.json`
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/runs/eval/d4_eval_report_replay.json`
- 日期：2026-02-26
- 适用范围：D5 及后续所有 D4 质量评估、30天 Go/No-Go 窗口判断。
- 置信度：0.98
- 标签：#d5 #dual-scope #legacy-replay #quality-baseline
- 状态：active

### 36) D5 关键踩坑：summary 文件会污染统计口径
- 结论：若 D4 直接 glob `runs/d3_reports/**/*.json`，会误把 `*_summary.json` 纳入输入，导致报告数/排除数偏差；必须在解析前过滤。
- 证据：修复前 quality `excluded_reports=24`，修复后为 23（与 legacy 报告数一致）。
- 来源：`/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/d4_eval_harness.py`（`resolve_inputs` 过滤逻辑）。
- 日期：2026-02-26
- 适用范围：所有基于文件 glob 的评估聚合任务。
- 置信度：0.99
- 标签：#pitfall #input-filter #eval-harness
- 状态：active


### 37) D5-1 首个真实 live 批次链路已落地（CR-V 抖音30条）
- 结论：项目已完成首个真实 `quality_baseline` 批次从多-sheet Excel 到 D4 主评估的端到端链路，批次号固定为 `live_20260226_crv_douyin_30`。
- 证据：payload/d3/sidecar/d4 报告文件均已生成，且 D4 `report_scope=quality_baseline`、`included_inputs=1`。
- 来源：
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/d5_live_baseline_adapter.py`
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/runs/eval/d4_eval_report_quality_live_20260226.json`
- 日期：2026-02-26
- 适用范围：后续所有 live 批次接入与单窗口质量评估。
- 置信度：0.98
- 标签：#d5-1 #live-batch #quality-baseline
- 状态：active

### 38) D5-1 关键操作纪律：live评估必须显式 --inputs
- 结论：为避免 smoke/replay 干扰，D4 在 live 场景必须用 `--inputs <live_report>` 精确指定输入，而不是依赖 glob。
- 证据：本次主报告 `included_inputs=1`、`excluded_reports=0`，实现严格口径隔离。
- 来源：`/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/runs/eval/d4_eval_report_quality_live_20260226.json`。
- 日期：2026-02-26
- 适用范围：live批次周报、Go/No-Go 单窗口判读。
- 置信度：0.99
- 标签：#scope-isolation #d4 #inputs
- 状态：active

### 39) D5-1 踩坑：D3->D5 并发会导致 sidecar 漏生成
- 结论：若 D3 产物尚未落盘即触发 D5 style_quota，会漏掉新批次并导致 D4 `style_quota_hit_rate` 误判为 MISSING。
- 证据：并发时 summary 仅有 smoke sidecar；串行后 live sidecar 正常生成且 hit_rate=0.6。
- 来源：本会话执行日志与 `quality_baseline_summary.json`。
- 日期：2026-02-26
- 适用范围：批处理编排、CI 执行顺序、自动化脚本并发控制。
- 置信度：0.99
- 标签：#pitfall #race-condition #style-sidecar
- 状态：active


### 40) D5-2 自动分派器已落地（A/B 两包）
- 结论：项目已具备“从修订任务单到执行分工包”的自动化能力，分配策略为 `p0_first_balanced`，优先清硬门禁且保持负载均衡。
- 证据：新增 `d5_assign_fix_tasks.py`，产出 `assignment_all.csv`、`assignment_A.md`、`assignment_B.md`、`assignment_summary.json`。
- 来源：
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/d5_assign_fix_tasks.py`
  - `/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/vnext-mvp/runs/eval/assignments/live_20260226/`
- 日期：2026-02-26
- 适用范围：后续 live 批次修订任务派工与执行管理。
- 置信度：0.99
- 标签：#d5-2 #assignment #p0-first #balanced
- 状态：active

### 41) D5-2 分派质量门槛：覆盖/唯一/确定性/均衡
- 结论：分派结果必须同时满足四项自检：全量覆盖、item 唯一、重复运行一致、P0 差值 <= 1；否则不可下发。
- 证据：本次 `self_check` 全通过，且 `p0_delta=1`、`weight_delta=0.0`。
- 来源：`assignment_summary.json`。
- 日期：2026-02-26
- 适用范围：分派器回归测试、CI门槛、团队执行前验收。
- 置信度：0.99
- 标签：#self-check #deterministic #assignment-gate
- 状态：active


### 42) D5 阶段已形成“日终归档文档”作为交接入口
- 结论：项目已建立日终可交接文档，明日执行可直接从归档文件进入，不再依赖口头同步。
- 证据：新增 `12-D5阶段进度归档_2026-02-26.md`，含完成项、指标、任务包入口、明日步骤与风险。
- 来源：`/Users/will/Desktop/RoadToAGI/文案部/00-重启调研/12-D5阶段进度归档_2026-02-26.md`。
- 日期：2026-02-26
- 适用范围：D5 后续每日收尾与次日协作接续。
- 置信度：0.99
- 标签：#handover #daily-archive #d5
- 状态：active

### 43) 路径问题根治策略（文案部唯一权威）
- 结论：文案部后续交付路径只允许两行模板：“原文件名纯文本”+“单反引号绝对路径纯文本”；禁止本地 Markdown 链接，禁止裸文件名列表（如 `- assignment_A.md`），禁止 ASCII/URL 编码映射兜底。
- 证据：用户在 2026-02-26 复现点击 `assignment_A.md` 为空白；同次核验显示真实文件存在而编码路径不存在；仓库级、`agent-engineer` 与全局 `/Users/will/.codex/AGENTS.md` 均已补充“禁本地 Markdown 链接 + 禁裸文件名列表”硬约束。
- 来源：本次根治与记忆整合（2026-02-26）。
- 日期：2026-02-26
- 适用范围：文案部全部新会话与交付汇报。
- 置信度：0.99
- 标签：#path-policy #root-cause #single-source-of-truth
- 状态：active
