#!/usr/bin/env python
"""AI 简报智能体 - 主入口

运行方式:
    python -m ai_news_agent.main
    或
    ai-news (安装后)
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


def setup_environment():
    """设置环境变量"""
    # 加载 .env 文件
    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # 尝试当前目录
        load_dotenv()
    
    # 检查必要的环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未设置 OPENAI_API_KEY（DeepSeek API Key）")
        print("   请在 .env 文件中配置")
        sys.exit(1)
    
    # 设置 DeepSeek API 默认值
    if not os.getenv("OPENAI_API_BASE"):
        os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com"
    if not os.getenv("OPENAI_MODEL_NAME"):
        os.environ["OPENAI_MODEL_NAME"] = "deepseek-chat"


def send_email_report(report_path: str):
    """发送邮件报告"""
    from ai_news_agent.tools.push_tool import PushTool
    
    if not os.path.exists(report_path):
        print(f"⚠️  报告文件不存在: {report_path}")
        return
    
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    title = f"📰 AI 简报 - {datetime.now().strftime('%Y-%m-%d')}"
    
    push_tool = PushTool()
    result = push_tool._run(title=title, content=content, method="email")
    print(result)


def run():
    """运行 AI 简报智能体"""
    print("=" * 60)
    print("🤖 AI 简报智能体启动")
    print(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 设置环境
    setup_environment()
    
    # 确保输出目录存在
    os.makedirs("reports", exist_ok=True)
    
    # 导入并运行 Crew
    from ai_news_agent.crew import AINewsAgentCrew
    
    # 配置输入
    inputs = {
        "target_subreddits": "LocalLLaMA, ArtificialIntelligence, singularity, MachineLearning, ChatGPT"
    }
    
    print("\n🔍 开始抓取资讯...")
    print(f"📌 Reddit 版块: {inputs['target_subreddits']}")
    print(f"📌 Hacker News: Top Stories")
    print("-" * 60)
    
    try:
        # 创建并执行 Crew
        crew_instance = AINewsAgentCrew()
        result = crew_instance.crew().kickoff(inputs=inputs)
        
        print("\n" + "=" * 60)
        print("✅ 简报生成完成!")
        
        report_path = "reports/daily_report.md"
        print(f"📄 报告已保存到: {report_path}")
        
        # 发送邮件
        print("\n📧 正在发送邮件...")
        send_email_report(report_path)
        
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"\n❌ 执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_scheduled():
    """运行定时任务模式"""
    import schedule
    import time
    
    print("⏰ 定时任务模式启动")
    print("   每天 09:30 自动执行")
    print("   按 Ctrl+C 退出")
    
    # 每天早上9:30执行
    schedule.every().day.at("09:30").do(run)
    
    # 启动时先执行一次
    print("\n🚀 启动时执行一次...")
    run()
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        run_scheduled()
    else:
        run()
