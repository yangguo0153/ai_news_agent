"""Hacker News 帖子抓取工具

使用官方 Hacker News API 抓取热门帖子。
API 文档: https://github.com/HackerNews/API
"""

import requests
from datetime import datetime, timezone
from typing import ClassVar, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class HackerNewsFetchInput(BaseModel):
    """Hacker News 抓取工具的输入参数"""
    limit: int = Field(
        default=30,
        description="抓取的帖子数量上限"
    )
    story_type: str = Field(
        default="top",
        description="帖子类型: 'top' (热门), 'new' (最新), 'best' (最佳)"
    )


class HackerNewsFetchTool(BaseTool):
    """抓取 Hacker News 热门帖子的工具"""
    
    name: str = "fetch_hackernews_posts"
    description: str = (
        "从 Hacker News 抓取热门科技资讯帖子。"
        "返回帖子的标题、链接、评分、评论数等信息。"
        "可以指定抓取数量和帖子类型。"
    )
    args_schema: Type[BaseModel] = HackerNewsFetchInput

    BASE_URL: ClassVar[str] = "https://hacker-news.firebaseio.com/v0"
    
    def _run(
        self,
        limit: int = 30,
        story_type: str = "top"
    ) -> str:
        """执行 Hacker News 帖子抓取"""
        
        # 获取帖子 ID 列表
        story_types = {
            "top": "topstories",
            "new": "newstories",
            "best": "beststories"
        }
        
        endpoint = story_types.get(story_type, "topstories")
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}.json",
                timeout=10
            )
            story_ids = response.json()[:limit]
        except Exception as e:
            return f"❌ 获取帖子列表失败: {str(e)}"
        
        # 获取每个帖子的详情
        posts = []
        for story_id in story_ids:
            try:
                resp = requests.get(
                    f"{self.BASE_URL}/item/{story_id}.json",
                    timeout=5
                )
                item = resp.json()
                
                if item and item.get("type") == "story":
                    # 计算帖子年龄
                    created_time = datetime.fromtimestamp(
                        item.get("time", 0),
                        tz=timezone.utc
                    )
                    age_hours = (
                        datetime.now(timezone.utc) - created_time
                    ).total_seconds() / 3600
                    
                    posts.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "hn_url": f"https://news.ycombinator.com/item?id={story_id}",
                        "score": item.get("score", 0),
                        "num_comments": item.get("descendants", 0),
                        "author": item.get("by", ""),
                        "age_hours": round(age_hours, 1)
                    })
            except Exception:
                continue
        
        # 格式化输出
        result = f"# Hacker News 热门帖子 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
        result += f"类型: {story_type} | 共 {len(posts)} 条\n\n"
        
        for i, post in enumerate(posts, 1):
            result += f"## {i}. {post['title']}\n"
            result += f"- 🔥 Score: {post['score']} | 💬 Comments: {post['num_comments']}\n"
            if post.get("url"):
                result += f"- 🌐 Link: {post['url']}\n"
            result += f"- 📰 HN: {post['hn_url']}\n"
            result += f"- 👤 Author: {post['author']} | ⏰ {post['age_hours']} hours ago\n\n"
        
        return result
