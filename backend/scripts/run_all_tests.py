#!/usr/bin/env python3
"""
全面测试脚本 - 测试EquityCompass的所有主要功能
"""

import requests
import json
import time
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5002"

def test_connection():
    """测试服务器连接"""
    print("🔗 测试服务器连接...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 服务器连接正常")
            return True
        else:
            print(f"❌ 服务器连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 服务器连接异常: {str(e)}")
        return False

def test_auth():
    """测试认证功能"""
    print("\n🔐 测试认证功能...")
    
    # 测试登录页面
    try:
        response = requests.get(f"{BASE_URL}/auth/login")
        if response.status_code == 200:
            print("✅ 登录页面正常")
        else:
            print(f"❌ 登录页面异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 登录页面测试失败: {str(e)}")

def test_stocks():
    """测试股票相关功能"""
    print("\n📈 测试股票功能...")
    
    # 测试股票列表
    try:
        response = requests.get(f"{BASE_URL}/stocks/")
        if response.status_code == 200:
            print("✅ 股票列表页面正常")
        else:
            print(f"❌ 股票列表页面异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 股票列表测试失败: {str(e)}")
    
    # 测试添加自定义股票页面
    try:
        response = requests.get(f"{BASE_URL}/stocks/add-custom")
        if response.status_code == 200:
            print("✅ 添加自定义股票页面正常")
        else:
            print(f"❌ 添加自定义股票页面异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 添加自定义股票页面测试失败: {str(e)}")

def test_analysis():
    """测试分析功能"""
    print("\n🤖 测试分析功能...")
    
    # 测试分析页面
    try:
        response = requests.get(f"{BASE_URL}/analysis/")
        if response.status_code == 200:
            print("✅ 分析页面正常")
        else:
            print(f"❌ 分析页面异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 分析页面测试失败: {str(e)}")
    
    # 测试任务列表
    try:
        response = requests.get(f"{BASE_URL}/analysis/tasks")
        if response.status_code == 200:
            print("✅ 任务列表页面正常")
        else:
            print(f"❌ 任务列表页面异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 任务列表测试失败: {str(e)}")

def test_reports():
    """测试报告功能"""
    print("\n📊 测试报告功能...")
    
    # 测试报告列表
    try:
        response = requests.get(f"{BASE_URL}/reports/")
        if response.status_code == 200:
            print("✅ 报告列表页面正常")
        else:
            print(f"❌ 报告列表页面异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 报告列表测试失败: {str(e)}")

def test_api_endpoints():
    """测试API端点"""
    print("\n🔌 测试API端点...")
    
    # 测试获取股票列表API
    try:
        response = requests.get(f"{BASE_URL}/api/stocks")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 股票API正常，返回 {len(data.get('stocks', []))} 只股票")
        else:
            print(f"❌ 股票API异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 股票API测试失败: {str(e)}")
    
    # 测试获取任务列表API
    try:
        response = requests.get(f"{BASE_URL}/api/tasks")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 任务API正常，返回 {len(data.get('tasks', []))} 个任务")
        else:
            print(f"❌ 任务API异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 任务API测试失败: {str(e)}")

def test_database():
    """测试数据库功能"""
    print("\n🗄️ 测试数据库功能...")
    
    try:
        from app import create_app, db
        from app.models.stock import Stock
        
        app = create_app()
        with app.app_context():
            # 测试数据库连接
            stocks_count = Stock.query.count()
            print(f"✅ 数据库连接正常，共有 {stocks_count} 只股票")
            
            # 测试内置股票
            builtin_stocks = Stock.query.filter_by(is_builtin=True).count()
            print(f"✅ 内置股票: {builtin_stocks} 只")
            
            # 测试自定义股票
            custom_stocks = Stock.query.filter_by(is_builtin=False).count()
            print(f"✅ 自定义股票: {custom_stocks} 只")
            
    except Exception as e:
        print(f"❌ 数据库测试失败: {str(e)}")

def test_file_system():
    """测试文件系统"""
    print("\n📁 测试文件系统...")
    
    # 检查必要的目录
    directories = [
        'data/reports',
        'data/tasks',
        'data/usage',
        'logs'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ 目录存在: {directory}")
        else:
            print(f"❌ 目录不存在: {directory}")
    
    # 检查日志文件
    if os.path.exists('logs/app.log'):
        print("✅ 应用日志文件存在")
    else:
        print("❌ 应用日志文件不存在")

def main():
    """主测试函数"""
    print("🚀 开始全面测试 EquityCompass 系统...")
    print("=" * 50)
    
    # 测试服务器连接
    if not test_connection():
        print("❌ 服务器未启动，请先启动应用")
        return
    
    # 测试各个功能模块
    test_auth()
    test_stocks()
    test_analysis()
    test_reports()
    test_api_endpoints()
    test_database()
    test_file_system()
    
    print("\n" + "=" * 50)
    print("🎉 全面测试完成！")
    print("如果所有测试都通过，说明系统运行正常。")
    print("如果有失败的测试，请检查相应的功能模块。")

if __name__ == "__main__":
    main()
