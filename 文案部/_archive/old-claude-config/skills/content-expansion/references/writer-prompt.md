# Writer Agent 提示词模板

> 主 Agent 为每个 Writer 动态拼装此模板后发出。`{placeholder}` 由编排器替换。

---

## Prompt

```
# 任务

写 1 篇{platform}汽车文案。严格按照下方参数、数据和规则执行，不做任何额外发挥。

## 你的分配参数

- 风格: {style} — {style_description}
- 角度: {angle} — {angle_description}
- 话题: {topic}
- 开头类型: {opening} — {opening_description}
- 论证结构: {structure} — {structure_description}
- 核心数据点: {data_point}
- 收尾方式: {closing} — {closing_description}

## 产品数据（只能用这些，不许编造任何数字）

{seed_excerpt}

## 风格参考（学节奏和语气，不抄句子）

{style_sample}

## 开头参考（从变体库中选取，学习节奏，不抄）

{opening_samples}

## 段落过渡参考（从过渡句库中选取，替代AI默认过渡）

{transition_samples}

## 结尾参考（从变体库中选取，学习收尾方式）

{closing_samples}

## 本篇禁用（同批次其他文章已使用，必须避开）

{banned_phrases}

## 新增约束（文案部标准更新 2026-02-11）

1. **禁止能源类型词** — 全文不得出现"混动""e:HEV""燃油""插混""纯电""油车""电车"等能源类型描述。统一用"这款车""CR-V""它"指代。

2. **禁止时间限定词** — 不得出现"刚买""新车""老车主""开了X年""买的时候""当时"等暗示购车/用车时间的描述。保持时间中立。

3. **首句必须点题** — 文章开头第一句必须直接点明核心卖点或主题，禁止铺垫。例如：
   - ❌ "春节快到了，很多人准备开车回家..."（绕弯子）
   - ✅ "CR-V的保值率60.27%，这个数据背后有门道。"（直击主题）

4. **场景描述真实** — 禁止虚构过度具体的第三方观察场景，如：
   - ❌ "服务区看到旁边车的后备箱..."
   - ❌ "隔壁车位的车主跟我说..."
   - ✅ 改用：真实车主口述、行业数据、客观体验

## 10 条铁律（违反任何 1 条 = 不合格）

{ten_rules}

## 输出格式

{output_format}
```

---

## 输出格式定义

### 抖音

```
标题:
第一行（话题引入）
第二行（产品+卖点）
第三行（结论/数据/体验）

脚本:
[250-350字，口语化短句，每句≤25字]

发布文案: [15-30字] #话题1 #话题2 #话题3
```

### 今日头条

```
标题: [20-30字单行标题，含品牌+车型名]

正文:
[650-800字，分3-4个自然段，口语化，每句≤25字]
```

---

## 注入说明（供主 Agent 参考，不发给 Writer）

| 占位符                                    | 来源                                       | 长度控制        |
| ----------------------------------------- | ------------------------------------------ | --------------- |
| `{platform}`                              | Brief 中的平台                             | 抖音 / 今日头条 |
| `{style}` + `{style_description}`         | 分配表 + diversity-matrix.md 维度1         | ~20字           |
| `{angle}` + `{angle_description}`         | 分配表 + diversity-matrix.md 维度2         | ~20字           |
| `{topic}`                                 | 分配表维度3                                | ~10字           |
| `{opening}` + `{opening_description}`     | 分配表 + diversity-matrix.md 维度4         | ~20字           |
| `{structure}` + `{structure_description}` | 分配表 + diversity-matrix.md 维度5         | ~20字           |
| `{data_point}`                            | 分配表维度6                                | ~10字           |
| `{closing}` + `{closing_description}`     | 分配表 + diversity-matrix.md 维度7         | ~20字           |
| `{seed_excerpt}`                          | 种子库按 data_point 关键词截取             | ≤300字          |
| `{style_sample}`                          | 风格语料库中对应风格的 1 篇样本            | ≤500字          |
| `{opening_samples}`                       | 开头变体库中对应类型的2个样本（轮换选取）  | ≤160字          |
| `{transition_samples}`                    | 过渡句库中随机3个（同批次不重复）          | ≤120字          |
| `{closing_samples}`                       | 结尾变体库中对应类型的2个样本（轮换选取）  | ≤120字          |
| `{banned_phrases}`                        | 本批次已完成文章的开头首句+结尾末句+转折句 | 动态增长        |
| `{ten_rules}`                             | `references/10-rules.md` 全文              | ~380字          |
| `{output_format}`                         | 上方按平台选取的输出格式定义               | ~80字           |

**拼装后总 prompt ≈ 1600 字**（含语料参考），任何模型都能高效执行。
