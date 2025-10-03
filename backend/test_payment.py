#!/usr/bin/env python3
"""
支付系统测试脚本
"""
import requests
import json
import time

def test_payment_system():
    """测试支付系统"""
    base_url = "http://localhost:5002"
    
    print("🧪 开始测试支付系统...")
    
    # 1. 测试获取支付方式
    print("\n1. 测试获取支付方式...")
    try:
        response = requests.get(f"{base_url}/api/payment/methods")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                methods = data.get('data', {}).get('payment_methods', [])
                print(f"✅ 获取到 {len(methods)} 种支付方式:")
                for method in methods:
                    print(f"   - {method['name']} ({method['code']})")
            else:
                print(f"❌ 获取支付方式失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 2. 测试创建订单（需要登录）
    print("\n2. 测试创建订单...")
    print("⚠️  注意：此测试需要先登录系统")
    print("   请访问 http://localhost:5002/coin 手动测试支付功能")
    
    print("\n📋 手动测试步骤:")
    print("1. 访问 http://localhost:5002/coin")
    print("2. 选择金币套餐，点击'立即购买'")
    print("3. 选择支付方式（支付宝/微信/Stripe）")
    print("4. 在模拟支付对话框中选择'支付成功'")
    print("5. 验证金币是否到账")
    
    print("\n🎉 支付系统测试完成！")

if __name__ == "__main__":
    test_payment_system()
