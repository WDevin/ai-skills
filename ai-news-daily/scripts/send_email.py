#!/usr/bin/env python3
"""
邮件发送模块 - 发送 AI 新闻日报到邮箱
支持 SMTP 发送，兼容 QQ邮箱、163邮箱、Gmail 等
"""

import smtplib
import os
import argparse
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


class EmailSender:
    """邮件发送器"""
    
    # 常见邮箱 SMTP 配置
    SMTP_CONFIGS = {
        'qq': {
            'server': 'smtp.qq.com',
            'port': 587,
            'use_tls': True
        },
        '163': {
            'server': 'smtp.163.com',
            'port': 587,
            'use_tls': True
        },
        'gmail': {
            'server': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True
        },
        'outlook': {
            'server': 'smtp.office365.com',
            'port': 587,
            'use_tls': True
        },
        'yahoo': {
            'server': 'smtp.mail.yahoo.com',
            'port': 587,
            'use_tls': True
        }
    }
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None, 
                 username: str = None, password: str = None,
                 email_type: str = 'qq'):
        """
        初始化邮件发送器
        
        参数:
            smtp_server: SMTP 服务器地址
            smtp_port: SMTP 端口
            username: 邮箱账号
            password: 邮箱密码/授权码
            email_type: 邮箱类型 (qq/163/gmail/outlook)
        """
        self.username = username or os.environ.get('EMAIL_USER')
        self.password = password or os.environ.get('EMAIL_PASSWORD')
        
        # 自动检测邮箱类型
        if not smtp_server and self.username:
            email_type = self._detect_email_type(self.username)
            config = self.SMTP_CONFIGS.get(email_type, self.SMTP_CONFIGS['qq'])
            self.smtp_server = config['server']
            self.smtp_port = config['port']
            self.use_tls = config['use_tls']
        else:
            self.smtp_server = smtp_server
            self.smtp_port = smtp_port or 587
            self.use_tls = True
    
    def _detect_email_type(self, email: str) -> str:
        """根据邮箱地址自动检测类型"""
        if '@qq.com' in email:
            return 'qq'
        elif '@163.com' in email:
            return '163'
        elif '@gmail.com' in email:
            return 'gmail'
        elif '@outlook.com' in email or '@hotmail.com' in email:
            return 'outlook'
        elif '@yahoo.com' in email:
            return 'yahoo'
        return 'qq'
    
    def send_email(self, to_email: str, subject: str, content: str, 
                   content_type: str = 'html', attachment_path: str = None) -> bool:
        """
        发送邮件
        
        参数:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型 (html/plain)
            attachment_path: 附件路径
        """
        if not self.username or not self.password:
            print("错误：未配置邮箱账号或密码")
            print("请设置环境变量：EMAIL_USER 和 EMAIL_PASSWORD")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加邮件正文
            if content_type == 'html':
                msg.attach(MIMEText(content, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 添加附件
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                filename = os.path.basename(attachment_path)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{filename}"'
                )
                msg.attach(attachment)
            
            # 连接 SMTP 服务器并发送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"邮件发送成功！收件人: {to_email}")
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False


def read_news_file(file_path: str) -> str:
    """读取新闻文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return ""


def parse_news_items(content: str) -> list:
    """解析 Markdown 新闻内容为结构化数据（支持来源和公司标签）"""
    items = []
    lines = content.split('\n')
    
    current_item = None
    current_summary = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') and not line.startswith('### '):
            continue
        
        # 新闻标题 (### 开头，新格式)
        if line.startswith('### '):
            # 保存之前的新闻
            if current_item:
                current_item['summary'] = '\n'.join(current_summary).strip()
                items.append(current_item)
            
            # 提取标题（去除序号如 "1. "）
            title = line.replace('### ', '').strip()
            # 移除开头的序号
            title = re.sub(r'^\d+\.\s*', '', title)
            
            current_item = {
                'title': title,
                'summary': '',
                'url': '',
                'source': '',
                'companies': []
            }
            current_summary = []
        
        # 旧格式兼容：新闻标题 (## 开头)
        elif line.startswith('## ') and not line.startswith('### '):
            if current_item:
                current_item['summary'] = '\n'.join(current_summary).strip()
                items.append(current_item)
            
            title = line.replace('## ', '').strip()
            title = re.sub(r'^\d+\.\s*', '', title)
            
            current_item = {
                'title': title,
                'summary': '',
                'url': '',
                'source': '',
                'companies': []
            }
            current_summary = []
        
        # 链接 [→ 阅读原文](url)
        elif line.startswith('[→ 阅读原文]') and current_item:
            match = re.search(r'\[→ 阅读原文\]\(([^)]+)\)', line)
            if match:
                current_item['url'] = match.group(1)
        
        # 元信息行（包含来源和公司）
        elif current_item and line.startswith('*') and ('📰' in line or '🏢' in line):
            # 提取来源
            source_match = re.search(r'📰\s*([^|·]+)', line)
            if source_match:
                current_item['source'] = source_match.group(1).strip()
            
            # 提取公司
            company_matches = re.findall(r'🏢\s*([^·|]+)', line)
            current_item['companies'] = [c.strip() for c in company_matches]
        
        # 摘要文字
        elif current_item and not line.startswith('---') and not line.startswith('[→') and not line.startswith('*'):
            # 移除 Markdown 格式
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line and not clean_line.startswith('//'):
                current_summary.append(clean_line)
    
    # 添加最后一条新闻
    if current_item:
        current_item['summary'] = '\n'.join(current_summary).strip()
        items.append(current_item)
    
    return items


def get_category_icon(title: str) -> str:
    """根据标题内容返回分类图标"""
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['发布', 'launch', 'release', '新品', '推出']):
        return ('🚀', '产品发布', '#e74c3c')
    elif any(kw in title_lower for kw in ['研究', 'paper', 'research', '论文', '学术']):
        return ('📚', '学术研究', '#3498db')
    elif any(kw in title_lower for kw in ['融资', 'funding', '投资', 'million', 'billion']):
        return ('💰', '投融资', '#27ae60')
    elif any(kw in title_lower for kw in ['政策', 'regulation', '法律', '监管', 'policy']):
        return ('⚖️', '政策法规', '#9b59b6')
    elif any(kw in title_lower for kw in ['安全', 'safety', 'security', '隐私']):
        return ('🔒', '安全隐私', '#f39c12')
    elif any(kw in title_lower for kw in ['应用', '应用案例', '案例', 'case', 'partner']):
        return ('💼', '商业应用', '#1abc9c')
    else:
        return ('🤖', 'AI 动态', '#34495e')


def generate_professional_html(news_items: list, date_str: str) -> str:
    """生成专业的新闻邮件 HTML 模板"""
    
    # 分类颜色映射
    category_colors = {
        '产品发布': '#e74c3c',
        '学术研究': '#3498db',
        '投融资': '#27ae60',
        '政策法规': '#9b59b6',
        '安全隐私': '#f39c12',
        '商业应用': '#1abc9c',
        'AI 动态': '#34495e'
    }
    
    # 公司颜色映射（热门公司）
    company_colors = {
        'OpenAI': '#10a37f',
        'Google': '#4285f4',
        'Anthropic': '#cc785c',
        'Meta': '#0668e1',
        'Microsoft': '#00a4ef',
        'NVIDIA': '#76b900',
        '阿里巴巴': '#ff6a00',
        '字节跳动': '#1f76ff',
        '百度': '#2932e1',
        '腾讯': '#0052d9',
        '华为': '#cf0a2c',
        '智谱 AI': '#2c5aa0',
        '月之暗面': '#000000',
    }
    
    def get_company_color(company: str) -> str:
        return company_colors.get(company, '#6c757d')
    
    # 生成新闻条目 HTML
    news_html = []
    for i, item in enumerate(news_items, 1):
        icon, category, color = get_category_icon(item['title'])
        summary = item['summary'][:200] + '...' if len(item['summary']) > 200 else item['summary']
        
        # 构建来源和公司标签
        meta_tags = []
        
        # 来源标签
        if item.get('source'):
            meta_tags.append(f'<span style="background-color: #f0f0f0; padding: 2px 8px; border-radius: 10px; font-size: 11px; color: #666; margin-right: 8px;">📰 {item["source"]}</span>')
        
        # 公司标签
        for company in item.get('companies', [])[:3]:  # 最多显示3个
            company_color = get_company_color(company)
            meta_tags.append(f'<span style="background-color: {company_color}15; padding: 2px 8px; border-radius: 10px; font-size: 11px; color: {company_color}; margin-right: 8px;">🏢 {company}</span>')
        
        meta_html = ''.join(meta_tags) if meta_tags else ''
        
        news_html.append(f'''
        <tr>
            <td style="padding: 0 30px 25px 30px;">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                        <td style="border-left: 4px solid {color}; padding-left: 15px;">
                            <!-- 分类标签 -->
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td style="background-color: {color}15; padding: 4px 10px; border-radius: 12px;">
                                        <span style="font-size: 12px; color: {color}; font-weight: 600;">{icon} {category}</span>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- 标题 -->
                            <h2 style="margin: 12px 0 8px 0; font-size: 18px; line-height: 1.4; color: #1a1a1a; font-weight: 600;">
                                <a href="{item['url']}" target="_blank" style="color: #1a1a1a; text-decoration: none;">{item['title']}</a>
                            </h2>
                            
                            <!-- 摘要 -->
                            <p style="margin: 0 0 12px 0; font-size: 14px; line-height: 1.6; color: #555;">
                                {summary}
                            </p>
                            
                            <!-- 来源和公司标签 -->
                            <p style="margin: 0 0 10px 0;">
                                {meta_html}
                            </p>
                            
                            <!-- 阅读更多 -->
                            <a href="{item['url']}" target="_blank" style="display: inline-block; font-size: 13px; color: {color}; text-decoration: none; font-weight: 500;">
                                阅读全文 →
                            </a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        ''')
    
    news_list = '\n'.join(news_html)
    
    # 完整的 HTML 模板
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 每日精选 - {date_str}</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;">
    <!-- 外层容器 -->
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <!-- 主内容区 -->
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640" style="max-width: 640px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    
                    <!-- Header 区域 -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                            <!-- Logo/标题 -->
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center">
                                <tr>
                                    <td style="padding-bottom: 15px;">
                                        <span style="font-size: 42px;">🤖</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <h1 style="margin: 0; font-size: 28px; color: #ffffff; font-weight: 700; letter-spacing: 1px;">AI DAILY</h1>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-top: 8px;">
                                        <p style="margin: 0; font-size: 14px; color: rgba(255,255,255,0.85); letter-spacing: 3px;">人工智能每日精选</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- 日期栏 -->
                    <tr>
                        <td style="background-color: #fafafa; padding: 20px 30px; border-bottom: 1px solid #eeeeee;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                <tr>
                                    <td style="font-size: 14px; color: #888; text-align: left;">
                                        📅 {date_str}
                                    </td>
                                    <td style="font-size: 14px; color: #888; text-align: right;">
                                        共 {len(news_items)} 条新闻
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- 导语 -->
                    <tr>
                        <td style="padding: 30px 30px 20px 30px;">
                            <p style="margin: 0; font-size: 15px; line-height: 1.7; color: #444;">
                                早上好！以下是今日最值得关注的 AI 行业动态，涵盖技术突破、产品发布、商业应用等多个维度。
                            </p>
                        </td>
                    </tr>
                    
                    <!-- 新闻列表 -->
                    {news_list}
                    
                    <!-- 分隔线 -->
                    <tr>
                        <td style="padding: 0 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                                <tr>
                                    <td style="border-top: 1px solid #eeeeee; padding-top: 30px;"></td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- 底部订阅信息 -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f8f9fa; border-radius: 8px;">
                                <tr>
                                    <td style="padding: 25px; text-align: center;">
                                        <p style="margin: 0 0 10px 0; font-size: 16px; color: #333; font-weight: 600;">💡 关于 AI DAILY</p>
                                        <p style="margin: 0; font-size: 13px; line-height: 1.6; color: #666;">
                                            每日精选全球 AI 领域最新动态，助您把握技术趋势。<br>
                                            每晚 8 点自动推送，如需退订请联系管理员。
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #2c3e50; padding: 25px 30px; text-align: center;">
                            <p style="margin: 0 0 8px 0; font-size: 13px; color: rgba(255,255,255,0.7);">
                                此邮件由 AI 自动生成，发送于 {datetime.now().strftime('%Y-%m-%d %H:%M')}
                            </p>
                            <p style="margin: 0; font-size: 12px; color: rgba(255,255,255,0.5);">
                                © 2026 AI News Daily. All rights reserved.
                            </p>
                        </td>
                    </tr>
                    
                </table>
                <!-- 主内容区结束 -->
                
                <!-- 底部间距 -->
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640" style="max-width: 640px;">
                    <tr>
                        <td style="padding: 20px; text-align: center;">
                            <p style="margin: 0; font-size: 12px; color: #999;">
                                如果邮件显示异常，请尝试在邮箱中点击"显示图片"
                            </p>
                        </td>
                    </tr>
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>'''
    
    return html


def markdown_to_html(markdown_content: str) -> str:
    """Markdown 转专业 HTML 邮件"""
    date_str = datetime.now().strftime('%Y年%m月%d日')
    
    # 解析新闻条目
    news_items = parse_news_items(markdown_content)
    
    if not news_items:
        # 如果没有解析到新闻，使用简单转换
        return generate_simple_html(markdown_content, date_str)
    
    # 生成专业模板
    return generate_professional_html(news_items, date_str)


def generate_simple_html(content: str, date_str: str) -> str:
    """简单 HTML 转换（备用）"""
    # 基础转换
    html = content
    html = html.replace('# ', '<h1>').replace('\n## ', '</p>\n<h2>').replace('\n### ', '</p>\n<h3>')
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    html = html.replace('\n\n', '</p>\n<p>')
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI 每日新闻</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
    <p>{html}</p>
</body>
</html>'''


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description='发送 AI 新闻邮件')
    parser.add_argument('--to', required=True, help='收件人邮箱')
    parser.add_argument('--subject', default=None, help='邮件主题')
    parser.add_argument('--file', required=True, help='新闻文件路径')
    parser.add_argument('--format', choices=['html', 'plain'], default='html', 
                       help='邮件格式')
    parser.add_argument('--attach', action='store_true', help='是否附加原文件')
    
    args = parser.parse_args()
    
    # 读取新闻内容
    content = read_news_file(args.file)
    if not content:
        print("错误：无法读取新闻文件")
        return
    
    # 设置主题
    subject = args.subject or f"🤖 AI 每日精选 - {datetime.now().strftime('%Y年%m月%d日')}"
    
    # 转换格式
    if args.format == 'html':
        email_content = markdown_to_html(content)
    else:
        email_content = content
    
    # 发送邮件
    sender = EmailSender()
    sender.send_email(
        to_email=args.to,
        subject=subject,
        content=email_content,
        content_type=args.format,
        attachment_path=args.file if args.attach else None
    )


if __name__ == '__main__':
    main()
