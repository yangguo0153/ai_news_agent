"""推送工具

支持多种推送方式：微信(Server酱)、邮件、本地文件保存。
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class PushInput(BaseModel):
    """推送工具的输入参数"""
    title: str = Field(description="推送标题")
    content: str = Field(description="推送内容 (Markdown 格式)")
    method: str = Field(
        default="file",
        description="推送方式: 'wechat' (Server酱), 'email', 'file' (本地保存)"
    )


class PushTool(BaseTool):
    """多渠道推送工具"""
    
    name: str = "push_notification"
    description: str = (
        "将生成的简报推送到指定渠道。"
        "支持微信(Server酱)、邮件、本地文件保存。"
    )
    args_schema: Type[BaseModel] = PushInput
    
    def _run(
        self,
        title: str,
        content: str,
        method: str = "file"
    ) -> str:
        """执行推送"""
        if method == "wechat":
            return self._push_wechat(title, content)
        elif method == "email":
            return self._push_email(title, content)
        else:
            return self._save_file(title, content)
    
    def _push_wechat(self, title: str, content: str) -> str:
        """通过 Server酱 推送到微信"""
        key = os.getenv("SERVERCHAN_KEY")
        if not key:
            return "❌ 推送失败: 未配置 SERVERCHAN_KEY"
        
        url = f"https://sctapi.ftqq.com/{key}.send"
        data = {
            "title": title,
            "desp": content
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            if result.get("code") == 0:
                return f"✅ 微信推送成功: {title}"
            else:
                return f"❌ 微信推送失败: {result.get('message', 'Unknown error')}"
        except Exception as e:
            return f"❌ 微信推送异常: {str(e)}"
    
    def _push_email(self, title: str, content: str) -> str:
        """通过邮件推送"""
        host = os.getenv("SMTP_HOST")
        port = int(os.getenv("SMTP_PORT", "465"))
        user = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASSWORD")
        to_email = os.getenv("EMAIL_TO")
        
        if not all([host, user, password, to_email]):
            return "❌ 推送失败: 邮件配置不完整"
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = title
            msg["From"] = user
            msg["To"] = to_email
            
            # 添加纯文本和 HTML 版本
            text_part = MIMEText(content, "plain", "utf-8")
            html_content = self._markdown_to_html(content)
            html_part = MIMEText(html_content, "html", "utf-8")
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # 根据端口选择连接方式
            server = None
            try:
                if port == 465:
                    # SSL 连接
                    server = smtplib.SMTP_SSL(host, port, timeout=30)
                else:
                    # TLS 连接 (587)
                    server = smtplib.SMTP(host, port, timeout=30)
                    server.starttls()
                
                server.login(user, password)
                server.sendmail(user, to_email, msg.as_string())
                
                # 尝试正常关闭
                try:
                    server.quit()
                except Exception:
                    # 忽略退出时的错误（如 QQ 邮箱可能返回非标响应）
                    pass
            except Exception as e:
                raise e
            finally:
                if server:
                    try:
                        server.close()
                    except Exception:
                        pass
            
            return f"✅ 邮件推送成功: {title} -> {to_email}"
        except Exception as e:
            return f"❌ 邮件推送异常: {str(e)}"
    
    def _save_file(self, title: str, content: str) -> str:
        """保存到本地文件"""
        from datetime import datetime
        
        # 确保目录存在
        os.makedirs("reports", exist_ok=True)
        
        filename = f"reports/daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(content)
            return f"✅ 文件保存成功: {filename}"
        except Exception as e:
            return f"❌ 文件保存失败: {str(e)}"
    
    def _markdown_to_html(self, markdown: str) -> str:
        """将 Markdown 转换为精美的 Newsletter HTML 邮件"""
        import re
        
        # 移除 markdown 代码块包装（如果有）
        markdown = re.sub(r'^```markdown\s*\n?', '', markdown)
        markdown = re.sub(r'\n?```\s*$', '', markdown)
        
        html = markdown
        
        # 处理代码块 (``` 包裹的内容)
        html = re.sub(
            r'```(\w*)\n(.*?)```',
            r'<pre style="background: #1e1e2e; border-radius: 8px; padding: 16px; overflow-x: auto; font-family: \'SF Mono\', Monaco, monospace; font-size: 13px; color: #cdd6f4; margin: 16px 0;"><code>\2</code></pre>',
            html,
            flags=re.DOTALL
        )
        
        # 处理行内代码
        html = re.sub(
            r'`([^`]+)`',
            r'<code style="background: rgba(139, 92, 246, 0.15); color: #a78bfa; padding: 2px 6px; border-radius: 4px; font-family: \'SF Mono\', Monaco, monospace; font-size: 0.9em;">\1</code>',
            html
        )
        
        # 处理标题
        html = re.sub(
            r"^# (.+)$",
            r'<h1 style="font-size: 28px; font-weight: 700; color: #f8fafc; margin: 0 0 8px 0; line-height: 1.3;">\1</h1>',
            html,
            flags=re.MULTILINE
        )
        html = re.sub(
            r"^## (.+)$",
            r'<div style="margin-top: 32px; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid rgba(148, 163, 184, 0.2);"><h2 style="font-size: 20px; font-weight: 600; color: #e2e8f0; margin: 0;">\1</h2></div>',
            html,
            flags=re.MULTILINE
        )
        html = re.sub(
            r"^### (.+)$",
            r'<h3 style="font-size: 16px; font-weight: 600; color: #cbd5e1; margin: 20px 0 8px 0;">\1</h3>',
            html,
            flags=re.MULTILINE
        )
        
        # 处理链接
        html = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            r'<a href="\2" style="color: #60a5fa; text-decoration: none; border-bottom: 1px solid rgba(96, 165, 250, 0.3); transition: all 0.2s;">\1</a>',
            html
        )
        
        # 处理粗体
        html = re.sub(r"\*\*([^*]+)\*\*", r"<strong style='color: #f1f5f9;'>\1</strong>", html)
        
        # 处理列表项 (- 开头)
        html = re.sub(
            r"^- (.+)$",
            r'<div style="display: flex; align-items: flex-start; margin: 8px 0; padding-left: 4px;"><span style="color: #8b5cf6; margin-right: 10px; font-weight: bold;">›</span><span style="color: #cbd5e1; line-height: 1.6;">\1</span></div>',
            html,
            flags=re.MULTILINE
        )
        
        # 处理水平线
        html = re.sub(
            r"^---+$",
            r'<hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.5), transparent); margin: 24px 0;">',
            html,
            flags=re.MULTILINE
        )
        
        # 处理段落（连续两个换行）
        html = html.replace("\n\n", '</p><p style="color: #94a3b8; line-height: 1.7; margin: 12px 0;">')
        html = html.replace("\n", "<br>")
        
        # 完整的 HTML 模板
        full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Vibe Coding 日报</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%); min-height: 100vh;">
    <div style="max-width: 680px; margin: 0 auto; padding: 40px 20px;">
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 32px;">
            <div style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #6366f1); padding: 12px 24px; border-radius: 50px; margin-bottom: 16px;">
                <span style="color: white; font-size: 14px; font-weight: 600; letter-spacing: 1px;">🚀 AI VIBE CODING</span>
            </div>
        </div>
        
        <!-- Main Content Card -->
        <div style="background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(10px); border-radius: 16px; padding: 32px; border: 1px solid rgba(148, 163, 184, 0.1); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);">
            <p style="color: #94a3b8; line-height: 1.7; margin: 12px 0;">
                {html}
            </p>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; margin-top: 32px; padding: 24px; color: #64748b; font-size: 13px;">
            <p style="margin: 0 0 8px 0;">Powered by <span style="color: #8b5cf6;">AI News Agent</span> 🤖</p>
            <p style="margin: 0; opacity: 0.7;">Stay curious, keep building.</p>
        </div>
    </div>
</body>
</html>'''
        
        return full_html
