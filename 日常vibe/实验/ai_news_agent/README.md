# AI 简报智能体

基于 CrewAI 框架的每日 AI 资讯聚合智能体，自动抓取 Reddit 论坛热门帖子并生成结构化简报。

## 功能特点

- 🔍 **智能抓取**: 自动抓取 Reddit AI 相关版块 (LocalLLaMA, ArtificialIntelligence, singularity)
- 🤖 **多 Agent 协作**: 社区观察员 + 技术分析师双 Agent 协同工作
- 📝 **结构化输出**: 生成 Markdown 格式的每日简报
- ⏰ **定时执行**: 支持配置定时任务，每日自动推送

## 快速开始

### 1. 安装依赖

```bash
cd 日常vibe/实验/ai_news_agent
pip install -e .
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Keys
```

**必需配置:**

- `OPENAI_API_KEY`: OpenAI API 密钥
- `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`: Reddit API 凭证

### 3. 运行

```bash
# 单次运行
python -m ai_news_agent.main

# 或使用命令行
ai-news
```

## 项目结构

```
.
├── src/ai_news_agent/
│   ├── main.py          # 入口文件
│   ├── crew.py          # Crew 定义
│   ├── config/
│   │   ├── agents.yaml  # Agent 配置
│   │   └── tasks.yaml   # Task 配置
│   └── tools/
│       ├── reddit_tool.py   # Reddit 抓取工具
│       └── push_tool.py     # 推送工具
└── reports/             # 生成的报告目录
```

## 获取 Reddit API 凭证

1. 访问 https://www.reddit.com/prefs/apps
2. 点击 "Create App" 或 "Create Another App"
3. 选择 "script" 类型
4. 填写信息后获取 Client ID 和 Secret

## License

MIT
