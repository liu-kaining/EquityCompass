#!/usr/bin/env python3
"""
测试邮件验证流程
"""
import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_auth_flow():
    """测试完整的认证流程"""
    print("🧪 开始测试邮件验证流程...")
    
    # 1. 发送验证码
    print("\n1️⃣ 发送验证码...")
    email = "test_flow@example.com"
    response = requests.post(f"{BASE_URL}/api/auth/send-code", 
                           json={"email": email})
    
    if response.status_code != 200:
        print(f"❌ 发送验证码失败: {response.status_code}")
        return False
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ 发送验证码失败: {data.get('message')}")
        return False
    
    code = data['data']['code']
    print(f"✅ 验证码发送成功: {code}")
    
    # 2. 验证验证码
    print("\n2️⃣ 验证验证码...")
    response = requests.post(f"{BASE_URL}/api/auth/verify-code", 
                           json={"email": email, "code": code})
    
    if response.status_code != 200:
        print(f"❌ 验证码验证失败: {response.status_code}")
        return False
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ 验证码验证失败: {data.get('message')}")
        return False
    
    print("✅ 验证码验证成功")
    print(f"   - 用户ID: {data['data']['user']['id']}")
    print(f"   - 用户邮箱: {data['data']['user']['email']}")
    print(f"   - Token类型: {data['data']['token_type']}")
    
    # 3. 访问仪表板
    print("\n3️⃣ 访问仪表板...")
    session = requests.Session()
    
    # 先进行验证码验证，这样session会被设置
    verify_response = session.post(f"{BASE_URL}/api/auth/verify-code", 
                                 json={"email": email, "code": code})
    
    if verify_response.status_code == 200:
        print("✅ Session设置成功")
    
    # 使用session cookies访问仪表板
    response = session.get(f"{BASE_URL}/dashboard/")
    
    if response.status_code == 200:
        if "欢迎回来" in response.text or "仪表板" in response.text:
            print("✅ 仪表板访问成功")
            print("   - 页面包含欢迎信息")
        else:
            print("⚠️  仪表板页面可能有问题")
            print(f"   - 响应内容长度: {len(response.text)}")
    elif response.status_code == 302:
        print("⚠️  仪表板重定向到登录页面")
    else:
        print(f"❌ 仪表板访问失败: {response.status_code}")
    
    # 4. 测试重新发送验证码
    print("\n4️⃣ 测试重新发送验证码...")
    time.sleep(2)  # 等待一下
    
    response = requests.post(f"{BASE_URL}/api/auth/send-code", 
                           json={"email": email})
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ 重新发送验证码成功")
        else:
            print(f"⚠️  重新发送验证码失败: {data.get('message')}")
    else:
        print(f"❌ 重新发送验证码失败: {response.status_code}")
    
    print("\n🎉 邮件验证流程测试完成！")
    return True

if __name__ == "__main__":
    test_auth_flow()
