#!/usr/bin/env python3
"""
测试报告统计功能
"""
import os
import sys
import requests
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def login():
    """登录获取session"""
    base_url = "http://localhost:5000"
    
    print("🔐 尝试登录...")
    
    # 创建session
    session = requests.Session()
    
    try:
        # 登录
        login_data = {
            'email': 'admin@example.com',
            'password': 'admin123'
        }
        
        response = session.post(f"{base_url}/auth/login", data=login_data)
        
        if response.status_code == 200:
            print("✅ 登录成功")
            return session
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return None

def test_statistics_api(session):
    """测试统计API"""
    base_url = "http://localhost:5000"
    
    print("🧪 开始测试报告统计功能...")
    
    # 1. 测试全局统计
    print("\n1. 测试全局统计API...")
    try:
        response = session.get(f"{base_url}/api/report-statistics/global-stats?days=30")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 全局统计API测试成功")
                print(f"   总报告数: {data['data']['total_reports']}")
                print(f"   总浏览次数: {data['data']['total_views']}")
                print(f"   总下载次数: {data['data']['total_downloads']}")
                print(f"   总分享次数: {data['data']['total_shares']}")
                print(f"   总收藏次数: {data['data']['total_favorites']}")
            else:
                print("❌ 全局统计API返回失败")
                print(f"   错误信息: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 全局统计API请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 全局统计API测试异常: {str(e)}")
    
    # 2. 测试每日统计
    print("\n2. 测试每日统计API...")
    try:
        response = session.get(f"{base_url}/api/report-statistics/daily-stats?days=7")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 每日统计API测试成功")
                print(f"   返回数据条数: {len(data['data'])}")
                if data['data']:
                    print(f"   最新日期: {data['data'][0]['date']}")
                    print(f"   最新浏览次数: {data['data'][0]['views']}")
                    print(f"   最新下载次数: {data['data'][0]['downloads']}")
            else:
                print("❌ 每日统计API返回失败")
                print(f"   错误信息: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 每日统计API请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 每日统计API测试异常: {str(e)}")
    
    # 3. 测试热门报告
    print("\n3. 测试热门报告API...")
    try:
        response = session.get(f"{base_url}/api/report-statistics/popular?limit=5&days=30")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 热门报告API测试成功")
                print(f"   返回报告数: {len(data['data'])}")
                if data['data']:
                    print(f"   最热门报告: {data['data'][0]['stock']['name']} ({data['data'][0]['stock']['code']})")
                    print(f"   浏览次数: {data['data'][0]['view_count']}")
                    print(f"   下载次数: {data['data'][0]['download_count']}")
            else:
                print("❌ 热门报告API返回失败")
                print(f"   错误信息: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 热门报告API请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 热门报告API测试异常: {str(e)}")
    
    # 4. 测试报告统计详情
    print("\n4. 测试报告统计详情API...")
    try:
        # 先获取一个报告ID（这里假设有报告ID为1）
        response = session.get(f"{base_url}/api/report-statistics/report/1")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 报告统计详情API测试成功")
                stats = data['data']
                print(f"   浏览次数: {stats['view_count']}")
                print(f"   下载次数: {stats['download_count']}")
                print(f"   分享次数: {stats['share_count']}")
                print(f"   收藏次数: {stats['favorite_count']}")
            else:
                print("❌ 报告统计详情API返回失败")
                print(f"   错误信息: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 报告统计详情API请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 报告统计详情API测试异常: {str(e)}")
    
    print("\n🎉 统计功能测试完成！")

def test_statistics_page(session):
    """测试统计页面"""
    base_url = "http://localhost:5000"
    
    print("\n🌐 测试统计页面...")
    
    try:
        response = session.get(f"{base_url}/reports/statistics")
        if response.status_code == 200:
            print("✅ 统计页面访问成功")
            if "报告统计" in response.text:
                print("✅ 页面内容正确")
            else:
                print("⚠️ 页面内容可能有问题")
        else:
            print(f"❌ 统计页面访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 统计页面测试异常: {str(e)}")

if __name__ == "__main__":
    print("🚀 开始测试报告统计功能...")
    
    # 登录
    session = login()
    if not session:
        print("❌ 登录失败，无法继续测试")
        sys.exit(1)
    
    # 测试API
    test_statistics_api(session)
    
    # 测试页面
    test_statistics_page(session)
    
    print("\n✨ 所有测试完成！")
