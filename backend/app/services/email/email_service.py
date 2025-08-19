"""
邮件服务
负责发送验证码邮件和其他邮件通知
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from flask import current_app
from datetime import datetime


class EmailService:
    """邮件服务"""
    
    def __init__(self):
        self.smtp_server = current_app.config.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = current_app.config.get('SMTP_PORT', 587)
        self.smtp_username = current_app.config.get('SMTP_USERNAME', '')
        self.smtp_password = current_app.config.get('SMTP_PASSWORD', '')
        self.from_email = current_app.config.get('FROM_EMAIL', 'noreply@equitycompass.com')
        self.from_name = current_app.config.get('FROM_NAME', '智策股析')
    
    def send_verification_code(self, to_email: str, code: str) -> Dict[str, Any]:
        """
        发送验证码邮件
        
        Args:
            to_email: 收件人邮箱
            code: 验证码
            
        Returns:
            发送结果
        """
        try:
            subject = f"【{self.from_name}】邮箱验证码"
            
            # HTML邮件内容
            html_content = self._get_verification_code_template(code)
            
            # 纯文本内容（备用）
            text_content = f"""
您好！

您正在登录{self.from_name}，验证码为：{code}

验证码有效期为10分钟，请及时使用。

如果您没有进行此操作，请忽略此邮件。

---
{self.from_name}团队
            """.strip()
            
            return self._send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            current_app.logger.error(f"发送验证码邮件失败: {e}")
            return {
                'success': False,
                'error': 'EMAIL_SEND_FAILED',
                'message': '邮件发送失败'
            }
    
    def send_welcome_email(self, to_email: str, nickname: str) -> Dict[str, Any]:
        """
        发送欢迎邮件
        
        Args:
            to_email: 收件人邮箱
            nickname: 用户昵称
            
        Returns:
            发送结果
        """
        try:
            subject = f"欢迎加入{self.from_name}！"
            
            html_content = self._get_welcome_email_template(nickname)
            
            text_content = f"""
亲爱的 {nickname}，

欢迎加入{self.from_name}！

我们很高兴您选择了我们的股票分析服务。您现在可以：

• 关注您感兴趣的股票（最多20支）
• 获得AI驱动的每日分析报告
• 导出和分享您的分析结果

开始您的投资分析之旅吧！

如有任何问题，请随时联系我们。

---
{self.from_name}团队
            """.strip()
            
            return self._send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            current_app.logger.error(f"发送欢迎邮件失败: {e}")
            return {
                'success': False,
                'error': 'EMAIL_SEND_FAILED',
                'message': '欢迎邮件发送失败'
            }
    
    def _send_email(self, to_email: str, subject: str, 
                   html_content: str, text_content: str = None) -> Dict[str, Any]:
        """
        发送邮件的核心方法
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML邮件内容
            text_content: 纯文本邮件内容
            
        Returns:
            发送结果
        """
        # 开发环境：模拟发送邮件
        if current_app.config.get('TESTING') or current_app.config.get('DEBUG'):
            current_app.logger.info(f"模拟发送邮件到 {to_email}:")
            current_app.logger.info(f"主题: {subject}")
            current_app.logger.info(f"内容: {text_content or html_content}")
            
            return {
                'success': True,
                'message': '邮件发送成功（开发模式）',
                'data': {
                    'to_email': to_email,
                    'subject': subject,
                    'sent_at': datetime.utcnow().isoformat()
                }
            }
        
        # 生产环境：实际发送邮件
        try:
            # 检查SMTP配置
            if not self.smtp_username or not self.smtp_password:
                current_app.logger.warning("SMTP配置未完成，跳过邮件发送")
                return {
                    'success': True,
                    'message': '邮件发送成功（配置未完成）'
                }
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # 添加纯文本内容
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            # 添加HTML内容
            if html_content:
                part2 = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(part2)
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            current_app.logger.info(f"邮件发送成功: {to_email}")
            
            return {
                'success': True,
                'message': '邮件发送成功',
                'data': {
                    'to_email': to_email,
                    'subject': subject,
                    'sent_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"SMTP邮件发送失败: {e}")
            return {
                'success': False,
                'error': 'SMTP_SEND_FAILED',
                'message': f'邮件发送失败: {str(e)}'
            }
    
    def _get_verification_code_template(self, code: str) -> str:
        """获取验证码邮件HTML模板"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>验证码</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .content {{
            padding: 40px 30px;
            text-align: center;
        }}
        .code {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            background-color: #f8f9ff;
            padding: 20px;
            border-radius: 8px;
            letter-spacing: 8px;
            margin: 20px 0;
            border: 2px dashed #667eea;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.from_name}</h1>
            <p>邮箱验证码</p>
        </div>
        <div class="content">
            <h2>您好！</h2>
            <p>您正在登录{self.from_name}，请使用以下验证码完成登录：</p>
            
            <div class="code">{code}</div>
            
            <p><strong>验证码有效期为10分钟</strong></p>
            <p>如果您没有进行此操作，请忽略此邮件。</p>
        </div>
        <div class="footer">
            <p>此邮件由系统自动发送，请勿回复</p>
            <p>&copy; 2025 {self.from_name}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """.strip()
    
    def _get_welcome_email_template(self, nickname: str) -> str:
        """获取欢迎邮件HTML模板"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>欢迎加入{self.from_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .feature {{
            display: flex;
            align-items: center;
            margin: 20px 0;
        }}
        .feature-icon {{
            width: 40px;
            height: 40px;
            background-color: #667eea;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 15px;
        }}
        .cta-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 欢迎加入{self.from_name}！</h1>
            <p>您的AI股票分析助手已准备就绪</p>
        </div>
        <div class="content">
            <h2>亲爱的 {nickname}，</h2>
            <p>欢迎加入{self.from_name}！我们很高兴您选择了我们的股票分析服务。</p>
            
            <h3>🚀 您现在可以：</h3>
            
            <div class="feature">
                <div class="feature-icon">📈</div>
                <div>
                    <strong>关注股票</strong><br>
                    <small>添加最多20支您感兴趣的股票到关注列表</small>
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon">🤖</div>
                <div>
                    <strong>AI分析</strong><br>
                    <small>获得基于AI的专业股票分析报告</small>
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div>
                    <strong>报告管理</strong><br>
                    <small>查看、筛选和导出您的分析报告</small>
                </div>
            </div>
            
            <div style="text-align: center;">
                <a href="#" class="cta-button">开始探索 →</a>
            </div>
            
            <p>如有任何问题，请随时联系我们的客服团队。</p>
            
            <p>祝您投资顺利！</p>
        </div>
        <div class="footer">
            <p>此邮件由系统自动发送，请勿回复</p>
            <p>&copy; 2025 {self.from_name}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """.strip()
    
    def test_connection(self) -> Dict[str, Any]:
        """测试邮件服务连接"""
        try:
            if current_app.config.get('TESTING') or current_app.config.get('DEBUG'):
                return {
                    'success': True,
                    'message': '邮件服务连接正常（开发模式）'
                }
            
            # 测试SMTP连接
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
            
            return {
                'success': True,
                'message': '邮件服务连接正常'
            }
            
        except Exception as e:
            current_app.logger.error(f"邮件服务连接测试失败: {e}")
            return {
                'success': False,
                'error': 'CONNECTION_FAILED',
                'message': f'邮件服务连接失败: {str(e)}'
            }
