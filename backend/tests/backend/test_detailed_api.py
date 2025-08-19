#!/usr/bin/env python3
"""
详细的API测试脚本
"""
import requests
import json
import time

def test_complete_flow():
    """测试完整的用户认证流程"""
    base_url = "http://localhost:5001"
    test_email = "test@example.com"
    
    print("🧪 开始用户认证API完整流程测试...\n")
    
    # 1. 测试发送验证码
    print("📧 步骤1: 发送验证码")
    send_result = test_send_code(base_url, test_email)
    if not send_result:
        return
    
    code = send_result['data']['code']
    print(f"✅ 获得验证码: {code}\n")
    
    # 2. 测试验证登录
    print("🔐 步骤2: 验证登录")
    token_result = test_verify_code(base_url, test_email, code)
    if not token_result:
        return
    
    access_token = token_result['data']['access_token']
    print(f"✅ 获得访问Token: {access_token[:50]}...\n")
    
    # 3. 测试获取用户资料
    print("👤 步骤3: 获取用户资料")
    profile_result = test_get_profile(base_url, access_token)
    if profile_result:
        print(f"✅ 用户资料: {json.dumps(profile_result['data'], indent=2, ensure_ascii=False)}\n")
    
    # 4. 测试更新用户资料
    print("✏️ 步骤4: 更新用户资料")
    update_result = test_update_profile(base_url, access_token, "API测试用户")
    if update_result:
        print(f"✅ 资料更新成功\n")
    
    # 5. 测试Token刷新
    print("🔄 步骤5: 刷新Token")
    refresh_token = token_result['data']['refresh_token']
    refresh_result = test_refresh_token(base_url, refresh_token)
    if refresh_result:
        new_token = refresh_result['data']['access_token']
        print(f"✅ 新Token: {new_token[:50]}...\n")
    
    # 6. 测试登出
    print("🚪 步骤6: 用户登出")
    logout_result = test_logout(base_url, access_token)
    if logout_result:
        print("✅ 登出成功\n")
    
    print("🎉 完整流程测试完成！")

def test_send_code(base_url, email):
    """测试发送验证码"""
    try:
        response = requests.post(
            f"{base_url}/api/auth/send-code",
            json={"email": email},
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and result['success']:
            return result
        else:
            print(f"   ❌ 发送验证码失败")
            return None
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return None

def test_verify_code(base_url, email, code):
    """测试验证登录"""
    try:
        response = requests.post(
            f"{base_url}/api/auth/verify-code",
            json={"email": email, "code": code},
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and result['success']:
            return result
        else:
            print(f"   ❌ 验证登录失败")
            return None
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return None

def test_get_profile(base_url, token):
    """测试获取用户资料"""
    try:
        response = requests.get(
            f"{base_url}/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and result['success']:
            return result
        else:
            print(f"   ❌ 获取资料失败")
            return None
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return None

def test_update_profile(base_url, token, nickname):
    """测试更新用户资料"""
    try:
        response = requests.put(
            f"{base_url}/api/auth/profile",
            json={"nickname": nickname},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and result['success']:
            return result
        else:
            print(f"   ❌ 更新资料失败")
            return None
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return None

def test_refresh_token(base_url, refresh_token):
    """测试刷新Token"""
    try:
        response = requests.post(
            f"{base_url}/api/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and result['success']:
            return result
        else:
            print(f"   ❌ 刷新Token失败")
            return None
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return None

def test_logout(base_url, token):
    """测试登出"""
    try:
        response = requests.post(
            f"{base_url}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        result = response.json()
        print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and result['success']:
            return result
        else:
            print(f"   ❌ 登出失败")
            return None
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return None

def test_error_cases():
    """测试错误情况"""
    base_url = "http://localhost:5001"
    print("\n🧪 测试错误处理...\n")
    
    # 测试无效邮箱
    print("📧 测试无效邮箱:")
    test_send_code(base_url, "invalid-email")
    
    print("\n🔐 测试错误验证码:")
    test_verify_code(base_url, "test@example.com", "000000")
    
    print("\n👤 测试无效Token:")
    test_get_profile(base_url, "invalid-token")

if __name__ == '__main__':
    test_complete_flow()
    test_error_cases()
