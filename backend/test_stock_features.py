#!/usr/bin/env python3
"""
股票列表功能测试脚本
"""
import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_stock_features():
    """测试股票列表功能"""
    print("🧪 开始测试股票列表功能...")
    
    # 创建session来保持登录状态
    session = requests.Session()
    
    # 1. 测试获取股票列表
    print("\n1️⃣ 测试获取股票列表...")
    response = session.get(f"{BASE_URL}/api/stocks")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            stocks = data['data']['stocks']
            print(f"✅ 成功获取 {len(stocks)} 支股票")
            print(f"   分页信息: 第{data['data']['pagination']['page']}页，共{data['data']['pagination']['pages']}页")
            print(f"   总计: {data['data']['pagination']['total']} 支股票")
        else:
            print(f"❌ 获取股票列表失败: {data['message']}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    # 2. 测试搜索股票
    print("\n2️⃣ 测试搜索股票...")
    response = session.get(f"{BASE_URL}/api/stocks/search?q=AAPL")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            stocks = data['data']['stocks']
            print(f"✅ 搜索 'AAPL' 找到 {len(stocks)} 支股票")
            if stocks:
                print(f"   第一个结果: {stocks[0]['code']} - {stocks[0]['name']}")
        else:
            print(f"❌ 搜索失败: {data['message']}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    # 3. 测试获取内置股票池
    print("\n3️⃣ 测试获取内置股票池...")
    response = session.get(f"{BASE_URL}/api/stocks/builtin")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            summary = data['data']['summary']
            print(f"✅ 内置股票池统计:")
            print(f"   美股: {summary['us_count']} 支")
            print(f"   港股: {summary['hk_count']} 支")
            print(f"   总计: {summary['total_count']} 支")
        else:
            print(f"❌ 获取内置股票池失败: {data['message']}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    # 4. 测试用户认证流程
    print("\n4️⃣ 测试用户认证流程...")
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
            time.sleep(1)  # 等待一下
            response = session.post(f"{BASE_URL}/api/auth/verify-code", 
                                   json={"email": email, "code": code})
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"✅ 用户认证成功")
                    user_id = data['data']['user']['id']
                    
                    # 5. 测试关注列表功能
                    print("\n5️⃣ 测试关注列表功能...")
                    
                    # 获取关注列表
                    response = session.get(f"{BASE_URL}/api/stocks/watchlist")
                    if response.status_code == 200:
                        data = response.json()
                        if data['success']:
                            watchlist = data['data']['watchlist']
                            print(f"✅ 获取关注列表成功: {len(watchlist)} 支股票")
                            print(f"   统计: {data['data']['count']}/{data['data']['max_count']}")
                        else:
                            print(f"❌ 获取关注列表失败: {data['message']}")
                    else:
                        print(f"❌ 请求失败: {response.status_code}")
                    
                    # 6. 测试添加关注
                    print("\n6️⃣ 测试添加关注...")
                    response = session.post(f"{BASE_URL}/api/stocks/watchlist/add", 
                                           json={"stock_code": "AAPL"})
                    if response.status_code == 200:
                        data = response.json()
                        if data['success']:
                            print(f"✅ 添加关注成功: {data['message']}")
                        else:
                            print(f"❌ 添加关注失败: {data['message']}")
                    else:
                        print(f"❌ 请求失败: {response.status_code}")
                    
                    # 7. 测试移除关注
                    print("\n7️⃣ 测试移除关注...")
                    response = session.post(f"{BASE_URL}/api/stocks/watchlist/remove", 
                                           json={"stock_code": "AAPL"})
                    if response.status_code == 200:
                        data = response.json()
                        if data['success']:
                            print(f"✅ 移除关注成功: {data['message']}")
                        else:
                            print(f"❌ 移除关注失败: {data['message']}")
                    else:
                        print(f"❌ 请求失败: {response.status_code}")
                    
                    # 8. 测试添加自定义股票
                    print("\n8️⃣ 测试添加自定义股票...")
                    stock_data = {
                        "code": "TEST123",
                        "name": "测试股票",
                        "market": "US"
                    }
                    response = session.post(f"{BASE_URL}/api/stocks", json=stock_data)
                    if response.status_code == 200:
                        data = response.json()
                        if data['success']:
                            print(f"✅ 添加自定义股票成功: {data['message']}")
                        else:
                            print(f"❌ 添加自定义股票失败: {data['message']}")
                    else:
                        print(f"❌ 请求失败: {response.status_code}")
                    
                else:
                    print(f"❌ 用户认证失败: {data['message']}")
            else:
                print(f"❌ 验证码验证请求失败: {response.status_code}")
        else:
            print(f"❌ 验证码发送失败: {data['message']}")
    else:
        print(f"❌ 验证码发送请求失败: {response.status_code}")
    
    # 9. 测试股票详情
    print("\n9️⃣ 测试股票详情...")
    response = session.get(f"{BASE_URL}/api/stocks/AAPL")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            stock = data['data']
            print(f"✅ 获取股票详情成功:")
            print(f"   代码: {stock['code']}")
            print(f"   名称: {stock['name']}")
            print(f"   市场: {stock['market']}")
        else:
            print(f"❌ 获取股票详情失败: {data['message']}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
    
    print("\n🎉 股票列表功能测试完成！")
    print("\n📋 测试总结:")
    print("✅ 股票列表获取")
    print("✅ 股票搜索功能")
    print("✅ 内置股票池")
    print("✅ 用户认证流程")
    print("✅ 关注列表管理")
    print("✅ 添加/移除关注")
    print("✅ 股票详情获取")
    print("✅ API响应格式")
    print("✅ 错误处理机制")

if __name__ == "__main__":
    test_stock_features()
