"""AI 简报智能体 Crew 定义

包含三个 Agent：
- reddit_scout: Reddit 社区观察员
- hackernews_scout: Hacker News 情报员
- tech_analyst: 技术分析师
"""

import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from .tools.reddit_tool import RedditFetchTool
from .tools.hackernews_tool import HackerNewsFetchTool
from .tools.twitter_tool import CrewTwitterSearchTool


def setup_proxy():
    """配置代理环境变量，确保 OpenAI SDK 能够使用代理"""
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    
    if https_proxy or http_proxy:
        proxy_url = https_proxy or http_proxy
        print(f"🌐 检测到代理: {proxy_url}")
        # OpenAI SDK 使用这些环境变量
        os.environ["OPENAI_PROXY"] = proxy_url
        os.environ["HTTPS_PROXY"] = proxy_url
        os.environ["HTTP_PROXY"] = proxy_url


def get_llm():
    """获取 LLM 配置，支持各种兼容 OpenAI 的 API 中转站
    
    使用 openai/ 前缀强制走 OpenAI 兼容模式，避免 CrewAI 尝试使用原生 SDK
    """
    # 确保代理配置正确
    setup_proxy()
    
    api_base = os.getenv("OPENAI_API_BASE") or "https://api.deepseek.com"
    model_name = os.getenv("OPENAI_MODEL_NAME") or "deepseek-chat"
    
    # 使用 openai/ 前缀强制走 OpenAI 兼容模式
    # 这样 CrewAI 不会尝试使用原生 Anthropic/DeepSeek SDK
    if not model_name.startswith("openai/"):
        model_name = f"openai/{model_name}"
    
    print(f"🤖 使用模型: {model_name}")
    print(f"🔗 API 地址: {api_base}")
    
    return LLM(
        model=model_name,
        base_url=api_base
    )


@CrewBase
class AINewsAgentCrew:
    """AI 简报智能体 Crew"""
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    def __init__(self):
        # 目标 subreddits (扩展版)
        self.target_subreddits = [
            "LocalLLaMA",
            "Cursor",
            "SideProject",
            "ArtificialIntelligence", 
            "singularity",
            "MachineLearning",
            "ChatGPT",
            "OpenAI"
        ]
        
        # 目标 Twitter 账号
        self.target_accounts = [
            "mckaywrigley",
            "rileybrown_ai",
            "gregisenberg",
            "karpathy",
            "amasad",
            "cursor_ai",
            "AnthropicAI",
            "MatthewBerman",
            "AndrewYNg",
            "ylecun",
            "sedielem"
        ]
        
        self.llm = get_llm()
    
    @agent
    def reddit_scout(self) -> Agent:
        """角色1: Reddit 社区观察员"""
        return Agent(
            config=self.agents_config["reddit_scout"],
            verbose=True,
            tools=[RedditFetchTool()],
            llm=self.llm
        )
    
    @agent
    def hackernews_scout(self) -> Agent:
        """角色2: Hacker News 情报员"""
        return Agent(
            config=self.agents_config["hackernews_scout"],
            verbose=True,
            tools=[HackerNewsFetchTool()],
            llm=self.llm
        )
        
    @agent
    def twitter_scout(self) -> Agent:
        """角色3: Twitter 情报员"""
        return Agent(
            config=self.agents_config["twitter_scout"],
            verbose=True,
            tools=[CrewTwitterSearchTool()],
            llm=self.llm
        )
    
    @agent
    def tech_analyst(self) -> Agent:
        """角色4: 技术分析师"""
        return Agent(
            config=self.agents_config["tech_analyst"],
            verbose=True,
            llm=self.llm
        )
    
    @task
    def gather_reddit_posts_task(self) -> Task:
        """任务1: 收集 Reddit 帖子"""
        return Task(
            config=self.tasks_config["gather_reddit_posts_task"]
        )
    
    @task
    def gather_hackernews_posts_task(self) -> Task:
        """任务2: 收集 Hacker News 帖子"""
        return Task(
            config=self.tasks_config["gather_hackernews_posts_task"]
        )
        
    @task
    def gather_twitter_posts_task(self) -> Task:
        """任务3: 收集 Twitter 帖子"""
        return Task(
            config=self.tasks_config["gather_twitter_posts_task"]
        )
    
    @task
    def analyze_and_report_task(self) -> Task:
        """任务4: 分析并生成报告"""
        return Task(
            config=self.tasks_config["analyze_and_report_task"],
            output_file="reports/daily_report.md"
        )
    
    @crew
    def crew(self) -> Crew:
        """组建 Crew 并执行"""
        return Crew(
            agents=self.agents,  # 自动由 @agent 装饰器创建
            tasks=self.tasks,    # 自动由 @task 装饰器创建
            process=Process.sequential,  # 顺序执行
            verbose=True
        )
