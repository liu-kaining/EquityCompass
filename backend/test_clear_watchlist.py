#!/usr/bin/env python3
"""
测试一键清空关注列表功能
"""
import requests
import time

BASE_URL = "http://localhost:5001"

def test_clear_watchlist():
    """测试一键清空关注列表功能"""
    print("🧹 开始测试一键清空关注列表功能...")
    
    # 创建session
    session = requests.Session()
    
    # 1. 登录
    print("\n1️⃣ 用户登录...")
    email = "test@example.com"
    
    # 发送验证码
    response = session.post(f"{BASE_URL}/api/auth/send-code", 
                           json={"email": email})
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            code = data['data']['code']
            print(f"✅ 验证码发送成功: {code}")
            
            # 验证码验证
            time.sleep(1)
            response = session.post(f"{BASE_URL}/api/auth/verify-code", 
                                   json={"email": email, "code": code})
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"✅ 用户登录成功")
                    
                    # 2. 添加多个股票到关注列表
                    print("\n2️⃣ 添加多个股票到关注列表...")
                    test_stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
                    
                    for stock in test_stocks:
                        response = session.post(f"{BASE_URL}/api/stocks/watchlist/add", 
                                               json={"stock_code": stock})
                        if response.status_code == 200:
                            data = response.json()
                            if data['success']:
                                print(f"✅ 添加 {stock} 成功")
                            else:
                                print(f"❌ 添加 {stock} 失败: {data['message']}")
                        else:
                            print(f"❌ 添加 {stock} 请求失败: {response.status_code}")
                    
                    # 3. 验证关注列表
                    print("\n3️⃣ 验证关注列表...")
                    response = session.get(f"{BASE_URL}/api/stocks/watchlist")
                    if response.status_code == 200:
                        data = response.json()
                        if data['success']:
                            watchlist = data['data']['watchlist']
                            print(f"✅ 关注列表中有 {len(watchlist)} 支股票")
                            for item in watchlist:
                                print(f"   - {item['stock']['code']}: {item['stock']['name']}")
                                if 'added_at' in item and item['added_at']:
                                    print(f"     关注时间: {item['added_at']}")
                                else:
                                    print(f"     关注时间: 未知")
                        else:
                            print(f"❌ 获取关注列表失败: {data['message']}")
                    else:
                        print(f"❌ 请求失败: {response.status_code}")
                    
                    # 4. 测试一键清空
                    print("\n4️⃣ 测试一键清空...")
                    response = session.post(f"{BASE_URL}/api/stocks/watchlist/clear")
                    if response.status_code == 200:
                        data = response.json()
                        if data['success']:
                            print(f"✅ 一键清空成功: {data['message']}")
                            print(f"   删除数量: {data['data']['deleted_count']}")
                        else:
                            print(f"❌ 一键清空失败: {data['message']}")
                    else:
                        print(f"❌ 请求失败: {response.status_code}")
                    
                    # 5. 验证清空结果
                    print("\n5️⃣ 验证清空结果...")
                    response = session.get(f"{BASE_URL}/api/stocks/watchlist")
                    if response.status_code == 200:
                        data = response.json()
                        if data['success']:
                            watchlist = data['data']['watchlist']
                            print(f"✅ 清空后关注列表中有 {len(watchlist)} 支股票")
                            if len(watchlist) == 0:
                                print("✅ 关注列表已完全清空")
                            else:
                                print("❌ 关注列表未完全清空")
                        else:
                            print(f"❌ 获取关注列表失败: {data['message']}")
                    else:
                        print(f"❌ 请求失败: {response.status_code}")
                    
                else:
                    print(f"❌ 用户登录失败: {data['message']}")
            else:
                print(f"❌ 验证码验证失败: {response.status_code}")
        else:
            print(f"❌ 验证码发送失败: {data['message']}")
    else:
        print(f"❌ 验证码发送请求失败: {response.status_code}")
    
    print("\n🎉 一键清空功能测试完成！")

if __name__ == "__main__":
    test_clear_watchlist()
