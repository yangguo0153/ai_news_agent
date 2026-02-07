# 开发日志

## 待办

### 🔴 高优先级：Reddit 信源集成问题

**问题描述**：

- AI 新闻助手工作流 Agent 已完成部署，但目前**无法抓取 Reddit 内容**
- Reddit 是非常重要的信源，必须解决

**当前状态**：❌ 阻塞中（API 申请被拒）

**问题根因分析**：

1. 已提交 Reddit API 申请，但被拒绝
2. 怀疑原因：**账号环境不干净**（可能是之前账号的问题）

**下一步行动**：

- [ ] 查明 Reddit 拒绝 API 申请的具体原因
- [ ] 考虑使用新的/干净的 Reddit 账号重新申请
- [ ] 或探索其他替代方案（如通过其他方式获取 Reddit 内容）

**相关文件**：

- 工作流配置：`.github/workflows/daily_news.yml`（已预留 Reddit 环境变量）
- 项目代码：`ai_news_agent/`

**记录日期**：2026-01-28

## 2026-01-18

- ✅ **ai_news_agent** 部署到 GitHub Actions 成功
- 踩坑：子目录项目需要把 `.github` 移到仓库根目录
- 踩坑：Secrets 配置格式（不要带 `KEY=` 前缀）
- 踩坑：litellm 需要显式安装 fastapi
- 踩坑：API 中转站地址和模型名必须匹配
