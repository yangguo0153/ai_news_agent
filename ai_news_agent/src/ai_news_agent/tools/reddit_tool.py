"""Reddit 帖子抓取工具

使用 PRAW (Python Reddit API Wrapper) 抓取指定 subreddit 的热门帖子。
"""

import os
from datetime import datetime, timezone
from typing import Any, Type, Optional

import praw
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class RedditFetchInput(BaseModel):
    """Reddit 抓取工具的输入参数"""
    subreddits: list[str] = Field(
        description="要抓取的 subreddit 列表，例如 ['LocalLLaMA', 'ArtificialIntelligence']"
    )
    limit: int = Field(
        default=25,
        description="每个 subreddit 抓取的帖子数量上限"
    )
    time_filter: str = Field(
        default="day",
        description="时间过滤器: 'hour', 'day', 'week', 'month', 'year', 'all'"
    )


class RedditFetchTool(BaseTool):
    """抓取 Reddit subreddit 热门帖子的工具"""
    
    name: str = "fetch_subreddit_posts"
    description: str = (
        "从指定的 Reddit subreddit 抓取热门帖子。"
        "返回帖子的标题、链接、评分、评论数等信息。"
        "需要提供 subreddit 名称列表。"
    )
    args_schema: Type[BaseModel] = RedditFetchInput
    
    _reddit: Any = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_reddit()
    
    def _init_reddit(self):
        """初始化 Reddit API 客户端，支持代理配置"""
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "AINewsAgent/1.0")
        
        # 获取代理配置（优先级：REDDIT_PROXY_URL > HTTP_PROXY/HTTPS_PROXY）
        proxy_url = (
            os.getenv("REDDIT_PROXY_URL") or
            os.getenv("HTTPS_PROXY") or
            os.getenv("HTTP_PROXY") or
            os.getenv("https_proxy") or
            os.getenv("http_proxy")
        )
        
        # 如果配置了代理，创建带代理的 session
        requestor_kwargs = {}
        if proxy_url:
            print(f"🌐 使用代理访问 Reddit: {proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url}")
            session = requests.Session()
            session.proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            requestor_kwargs = {"session": session}
        else:
            print("⚠️  未配置代理，直接访问 Reddit（可能无法连接）")
        
        # 初始化 PRAW 客户端
        if client_id and client_secret:
            self._reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                requestor_kwargs=requestor_kwargs
            )
        else:
            # 只读模式（无需认证）
            self._reddit = praw.Reddit(
                client_id="placeholder",
                client_secret="placeholder",
                user_agent=user_agent,
                requestor_kwargs=requestor_kwargs
            )
    
    def _run(
        self,
        subreddits: list[str],
        limit: int = 25,
        time_filter: str = "day"
    ) -> str:
        """执行 Reddit 帖子抓取"""
        all_posts = []
        
        for subreddit_name in subreddits:
            try:
                subreddit = self._reddit.subreddit(subreddit_name)
                posts = subreddit.top(time_filter=time_filter, limit=limit)
                
                for post in posts:
                    # 计算帖子年龄
                    created_time = datetime.fromtimestamp(
                        post.created_utc, 
                        tz=timezone.utc
                    )
                    age_hours = (
                        datetime.now(timezone.utc) - created_time
                    ).total_seconds() / 3600
                    
                    post_data = {
                        "subreddit": subreddit_name,
                        "title": post.title,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "url": f"https://reddit.com{post.permalink}",
                        "external_url": post.url if not post.is_self else None,
                        "selftext": post.selftext[:500] if post.is_self else None,
                        "age_hours": round(age_hours, 1),
                        "flair": post.link_flair_text,
                    }
                    all_posts.append(post_data)
                    
            except Exception as e:
                all_posts.append({
                    "subreddit": subreddit_name,
                    "error": str(e)
                })
        
        # 按分数排序
        valid_posts = [p for p in all_posts if "error" not in p]
        valid_posts.sort(key=lambda x: x["score"], reverse=True)
        
        # 格式化输出
        result = f"# Reddit 热门帖子 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
        result += f"共抓取 {len(valid_posts)} 条帖子\n\n"
        
        for i, post in enumerate(valid_posts, 1):
            result += f"## {i}. [{post['subreddit']}] {post['title']}\n"
            result += f"- 🔥 Score: {post['score']} | 💬 Comments: {post['num_comments']}\n"
            result += f"- 🔗 Reddit: {post['url']}\n"
            if post.get("external_url"):
                result += f"- 🌐 External: {post['external_url']}\n"
            if post.get("flair"):
                result += f"- 🏷️ Flair: {post['flair']}\n"
            if post.get("selftext"):
                result += f"- 📝 Preview: {post['selftext'][:200]}...\n"
            result += f"- ⏰ Posted: {post['age_hours']} hours ago\n\n"
        
        return result
