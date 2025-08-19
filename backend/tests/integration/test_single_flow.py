#!/usr/bin/env python3
"""
单一流程测试
"""
import requests
import json

def test_single_auth_flow():
    """测试单一认证流程"""
    base_url = "http://localhost:5001"
    email = "single@test.com"
    
    try:
        # 1. 发送验证码
        print("📧 发送验证码...")
        send_response = requests.post(
            f"{base_url}/api/auth/send-code",
            json={"email": email},
            timeout=5
        )
        
        if send_response.status_code != 200:
            print(f"❌ 发送失败: {send_response.text}")
            return
        
        send_data = send_response.json()
        code = send_data['data']['code']
        print(f"✅ 验证码: {code}")
        
        # 2. 立即验证
        print("🔐 验证登录...")
        verify_response = requests.post(
            f"{base_url}/api/auth/verify-code",
            json={"email": email, "code": code},
            timeout=5
        )
        
        print(f"状态码: {verify_response.status_code}")
        print(f"响应: {json.dumps(verify_response.json(), indent=2, ensure_ascii=False)}")
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            if verify_data['success']:
                token = verify_data['data']['access_token']
                print(f"✅ 登录成功，Token: {token[:50]}...")
                
                # 3. 测试获取资料
                print("👤 获取用户资料...")
                profile_response = requests.get(
                    f"{base_url}/api/auth/profile",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )
                
                print(f"资料状态码: {profile_response.status_code}")
                print(f"资料响应: {json.dumps(profile_response.json(), indent=2, ensure_ascii=False)}")
                
                if profile_response.status_code == 200:
                    print("🎉 完整流程测试成功！")
                else:
                    print("❌ 获取资料失败")
            else:
                print("❌ 登录返回失败")
        else:
            print("❌ 登录请求失败")
    
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")

if __name__ == '__main__':
    test_single_auth_flow()
