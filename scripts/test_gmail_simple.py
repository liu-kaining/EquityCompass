#!/usr/bin/env python3
"""
简单的Gmail邮件测试脚本
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

def test_gmail_587():
    """测试端口587 (TLS)"""
    print("🔧 测试Gmail SMTP端口587 (TLS)...")
    
    try:
        # 配置
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        username = "liqianlkn@gmail.com"
        password = "vnrv auqx qued mkqw"
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['Subject'] = "Gmail SMTP测试 - 端口587"
        msg['From'] = username
        msg['To'] = "liukaining2021@163.com"
        
        text = "这是一封来自Gmail SMTP的测试邮件 (端口587)"
        msg.attach(MIMEText(text, 'plain', 'utf-8'))
        
        # 连接并发送
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(username, password)
            server.send_message(msg)
        
        print("✅ 端口587测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 端口587测试失败: {e}")
        return False

def test_gmail_465():
    """测试端口465 (SSL)"""
    print("🔧 测试Gmail SMTP端口465 (SSL)...")
    
    try:
        # 配置
        smtp_server = "smtp.gmail.com"
        smtp_port = 465
        username = "liqianlkn@gmail.com"
        password = "vnrv auqx qued mkqw"
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['Subject'] = "Gmail SMTP测试 - 端口465"
        msg['From'] = username
        msg['To'] = "liukaining2021@163.com"
        
        text = "这是一封来自Gmail SMTP的测试邮件 (端口465)"
        msg.attach(MIMEText(text, 'plain', 'utf-8'))
        
        # 连接并发送
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=10) as server:
            server.login(username, password)
            server.send_message(msg)
        
        print("✅ 端口465测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 端口465测试失败: {e}")
        return False

def test_connection():
    """测试基本连接"""
    print("🔧 测试Gmail SMTP基本连接...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.gmail.com', 587))
        sock.close()
        
        if result == 0:
            print("✅ 端口587连接正常")
            return True
        else:
            print("❌ 端口587连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def main():
    print("🚀 Gmail邮件服务测试")
    print("=" * 50)
    
    # 测试基本连接
    if not test_connection():
        print("❌ 网络连接有问题，请检查网络设置")
        return
    
    # 测试端口587
    success_587 = test_gmail_587()
    
    # 测试端口465
    success_465 = test_gmail_465()
    
    print("\n📊 测试结果:")
    print(f"端口587 (TLS): {'✅ 成功' if success_587 else '❌ 失败'}")
    print(f"端口465 (SSL): {'✅ 成功' if success_465 else '❌ 失败'}")
    
    if success_587 or success_465:
        print("\n🎉 邮件服务配置成功！")
        if success_587:
            print("推荐使用端口587 (TLS)")
        if success_465:
            print("备选使用端口465 (SSL)")
    else:
        print("\n❌ 所有端口测试都失败了")
        print("请检查:")
        print("1. 网络连接")
        print("2. 防火墙设置")
        print("3. Gmail应用专用密码")
        print("4. 两步验证是否开启")

if __name__ == "__main__":
    main()

