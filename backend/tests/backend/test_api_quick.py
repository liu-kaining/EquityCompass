#!/usr/bin/env python3
"""
快速API测试
"""
import requests
import json

def test_send_code():
    """测试发送验证码API"""
    url = "http://localhost:5001/api/auth/send-code"
    data = {"email": "test@example.com"}
    
    try:
        response = requests.post(url, json=data, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            result = response.json()
            if 'code' in result.get('data', {}):
                code = result['data']['code']
                print(f"\n验证码: {code}")
                test_verify_code("test@example.com", code)
            else:
                print("⚠️ 没有返回验证码")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_verify_code(email, code):
    """测试验证登录API"""
    url = "http://localhost:5001/api/auth/verify-code"
    data = {"email": email, "code": code}
    
    try:
        response = requests.post(url, json=data, timeout=5)
        print(f"\n验证API状态码: {response.status_code}")
        print(f"验证API响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ 验证请求失败: {e}")

if __name__ == '__main__':
    test_send_code()
