#!/usr/bin/env python3
"""
Gmail邮件服务测试脚本
用于测试Gmail SMTP配置是否正确
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_gmail_smtp():
    """测试Gmail SMTP连接和发送"""
    
    print("📧 Gmail邮件服务测试")
    print("=" * 50)
    
    # 从环境变量获取配置
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', '')
    from_name = os.getenv('FROM_NAME', '智策股析')
    
    # 检查配置
    if not smtp_username or not smtp_password:
        print("❌ 错误: 请先配置SMTP_USERNAME和SMTP_PASSWORD环境变量")
        print("\n配置示例:")
        print("export SMTP_USERNAME=your-email@gmail.com")
        print("export SMTP_PASSWORD=your-16-digit-app-password")
        return False
    
    # 获取测试邮箱
    test_email = input("请输入测试邮箱地址: ").strip()
    if not test_email:
        print("❌ 错误: 请输入有效的邮箱地址")
        return False
    
    print(f"\n📋 配置信息:")
    print(f"SMTP服务器: {smtp_server}:{smtp_port}")
    print(f"发件人: {smtp_username}")
    print(f"收件人: {test_email}")
    
    try:
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"【{from_name}】邮件服务测试"
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = test_email
        
        # HTML内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>邮件服务测试</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .success {{
                    color: #28a745;
                    font-weight: bold;
                }}
                .info {{
                    background-color: #e7f3ff;
                    border: 1px solid #b3d9ff;
                    border-radius: 4px;
                    padding: 15px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 邮件服务测试成功！</h1>
                    <p>{from_name} - Gmail SMTP配置正常</p>
                </div>
                
                <h2>测试信息</h2>
                <div class="info">
                    <p><strong>测试时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>SMTP服务器:</strong> {smtp_server}:{smtp_port}</p>
                    <p><strong>发件人:</strong> {smtp_username}</p>
                    <p><strong>收件人:</strong> {test_email}</p>
                </div>
                
                <p class="success">✅ 恭喜！你的Gmail邮件服务配置成功！</p>
                
                <p>现在你可以：</p>
                <ul>
                    <li>发送验证码邮件给用户</li>
                    <li>发送欢迎邮件给新用户</li>
                    <li>发送系统通知邮件</li>
                </ul>
                
                <p>如果这是生产环境，请确保：</p>
                <ul>
                    <li>使用应用专用密码（不是账户密码）</li>
                    <li>开启了两步验证</li>
                    <li>配置了正确的发件人邮箱</li>
                </ul>
                
                <hr>
                <p style="color: #666; font-size: 12px;">
                    此邮件由 {from_name} 邮件服务测试脚本自动发送
                </p>
            </div>
        </body>
        </html>
        """
        
        # 纯文本内容
        text_content = f"""
邮件服务测试成功！

测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
SMTP服务器: {smtp_server}:{smtp_port}
发件人: {smtp_username}
收件人: {test_email}

✅ 恭喜！你的Gmail邮件服务配置成功！

现在你可以：
• 发送验证码邮件给用户
• 发送欢迎邮件给新用户
• 发送系统通知邮件

如果这是生产环境，请确保：
• 使用应用专用密码（不是账户密码）
• 开启了两步验证
• 配置了正确的发件人邮箱

---
此邮件由 {from_name} 邮件服务测试脚本自动发送
        """.strip()
        
        # 添加内容
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        print(f"\n📤 正在发送测试邮件...")
        
        # 连接SMTP服务器
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # 启用TLS加密
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print("✅ 邮件发送成功！")
        print(f"📧 请检查邮箱 {test_email} 的收件箱")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ 认证失败: {e}")
        print("\n可能的原因:")
        print("1. 应用专用密码错误")
        print("2. 未开启两步验证")
        print("3. 用户名或密码格式错误")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP错误: {e}")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def main():
    """主函数"""
    print("🚀 智策股析 - Gmail邮件服务测试工具")
    print("=" * 50)
    
    # 检查是否在项目目录
    if not os.path.exists('backend'):
        print("❌ 错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 运行测试
    success = test_gmail_smtp()
    
    if success:
        print("\n🎉 测试完成！邮件服务配置正确。")
        print("\n📝 下一步:")
        print("1. 将配置添加到生产环境的 .env 文件")
        print("2. 重启应用服务")
        print("3. 测试用户注册流程")
    else:
        print("\n❌ 测试失败！请检查配置。")
        print("\n📖 配置指南:")
        print("1. 确保开启Gmail两步验证")
        print("2. 生成应用专用密码")
        print("3. 使用正确的SMTP配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
