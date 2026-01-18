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
        """简单的 Markdown 转 HTML"""
        # 基础转换
        html = markdown
        
        # 处理标题 (在处理换行符之前)
        import re
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        
        # 处理链接
        html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
        
        # 处理粗体
        html = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", html)
        
        # 基础转换
        html = html.replace("\n\n", "</p><p>")
        html = html.replace("\n", "<br>")
        
        return f"<html><body><p>{html}</p></body></html>"
