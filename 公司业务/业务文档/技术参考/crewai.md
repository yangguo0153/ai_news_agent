# CrewAI 使用笔记

## LLM 配置要点

- 使用 `openai/` 前缀强制走 OpenAI 兼容模式（如 `openai/gpt-4o`）
- 自定义 API 需设置 `base_url` 参数

## 常见问题

### 工具名称不匹配

- **现象**: Agent 调用工具失败
- **解决**: 确保 `tasks.yaml` 中引用的工具名与代码中的 Tool 类名一致
