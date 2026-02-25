# Agent Engineer Memory Index

## 目标
把每日 vibe coding 与项目开发，沉淀为可复用的内容资产，让 AI 越用越懂你。

## 三层结构
1. Layer 1 知识图谱：`memory/areas/**/items.json` + `summary.md`
2. Layer 2 每日时间线：`memory/daily/YYYY-MM-DD.md`
3. Layer 3 隐性知识：`memory/MEMORY.md`

### 当前 Layer 1 关键区
- `memory/areas/topics/content-angles/`
- `memory/areas/formulas/hook-patterns/`
- `memory/areas/channels/wechat/`
- `memory/areas/channels/douyin/`
- `memory/areas/profile/subject-object-actions/`（高价值胶囊：`date/fact/source/tags`）

## 渐进式读取顺序
1. `memory/PROFILE.md`
2. `memory/MEMORY.md`
3. 按任务加载 `memory/areas/*/*/summary.md`
4. 必要时再读 `items.json` 与最近 7 天 `memory/daily/*.md`

## 写入规则
- 每次执行后至少写入 1 条 Layer 2 记录。
- 结论进入 Layer 3 时，必须有证据与置信度。
- 旧结论不删除，只能标记 `superseded`。
