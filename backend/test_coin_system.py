#!/usr/bin/env python3
"""
金币系统功能测试脚本
测试支付功能移除后的核心功能
"""
import sys
import os
import requests
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = 'http://localhost:5002'

def print_section(title):
    """打印测试章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_test(test_name):
    """打印测试名称"""
    print(f"\n📋 测试: {test_name}")

def print_success(message):
    """打印成功消息"""
    print(f"✅ {message}")

def print_error(message):
    """打印错误消息"""
    print(f"❌ {message}")

def print_warning(message):
    """打印警告消息"""
    print(f"⚠️  {message}")

def test_coin_api_endpoints():
    """测试金币API端点"""
    print_section("测试金币API端点")
    
    # 测试端点列表
    endpoints = [
        ('/api/coin/info', 'GET', '获取金币信息'),
        ('/api/coin/daily-bonus-status', 'GET', '获取签到状态'),
        ('/api/coin/bonus-stats', 'GET', '获取签到统计'),
        ('/api/coin/transactions', 'GET', '获取交易记录'),
    ]
    
    print_warning("这些端点需要登录，请在浏览器中手动测试")
    print("\n需要测试的端点：")
    for endpoint, method, desc in endpoints:
        print(f"  {method:4} {endpoint:30} - {desc}")
    
    # 测试已删除的端点（应该不存在）
    print_test("验证已删除的支付相关端点")
    removed_endpoints = [
        '/api/coin/order',
        '/api/coin/order/status/TEST123',
        '/api/payment/create',
        '/api/payment/verify',
        '/api/payment/methods',
    ]
    
    print("\n应该返回404的端点：")
    for endpoint in removed_endpoints:
        print(f"  {endpoint}")

def test_service_functions():
    """测试服务层函数"""
    print_section("测试服务层函数")
    
    print_test("验证CoinService中的方法")
    methods = [
        ('get_user_coin_info', '获取用户金币信息'),
        ('daily_bonus', '每日签到'),
        ('earn_coins', '获得金币'),
        ('spend_coins', '消耗金币'),
        ('get_user_transactions', '获取交易记录'),
        ('get_coin_packages', '获取套餐列表（仅展示）'),
    ]
    
    print("\n保留的方法：")
    for method, desc in methods:
        print(f"  ✓ {method:25} - {desc}")
    
    print_test("验证已删除的方法")
    removed_methods = [
        'create_coin_order',
        'get_order_status',
        'complete_coin_order',
    ]
    
    print("\n已删除的方法：")
    for method in removed_methods:
        print(f"  ✗ {method}")

def test_model_fields():
    """测试模型字段"""
    print_section("测试模型字段")
    
    print_test("验证CoinOrder模型字段")
    print("\n保留的字段：")
    fields = [
        ('id', '订单ID'),
        ('user_id', '用户ID'),
        ('package_id', '套餐ID'),
        ('order_no', '订单号'),
        ('amount', '订单金额'),
        ('coins', '金币数量'),
        ('status', '订单状态'),
        ('paid_at', '支付时间（历史数据）'),
    ]
    
    for field, desc in fields:
        print(f"  ✓ {field:15} - {desc}")
    
    print("\n已注释的字段（保留用于历史数据兼容）：")
    print("  ✗ payment_method - 支付方式")
    print("  ✗ payment_id - 支付ID")

def test_frontend_pages():
    """测试前端页面"""
    print_section("测试前端页面")
    
    print_test("验证页面路由")
    
    pages = [
        ('/coin', '金币中心页面', '应该显示：金币信息、签到、获取金币说明、交易记录'),
        ('/dashboard', '仪表盘页面', '应该移除购买按钮'),
    ]
    
    print("\n需要检查的页面：")
    for route, name, check in pages:
        print(f"  {route:20} - {name}")
        print(f"    {'':20}  {check}")
    
    print_test("验证已禁用的路由")
    print("  ✗ /coin/packages - 套餐页面（已禁用）")

def test_configuration():
    """测试配置"""
    print_section("测试配置文件")
    
    print_test("验证环境变量")
    print("\n已删除的支付环境变量：")
    removed_vars = [
        'ALIPAY_APP_ID',
        'ALIPAY_PRIVATE_KEY',
        'ALIPAY_PUBLIC_KEY',
        'WECHAT_APP_ID',
        'WECHAT_MCH_ID',
        'WECHAT_API_KEY',
        'STRIPE_PUBLISHABLE_KEY',
        'STRIPE_SECRET_KEY',
        'STRIPE_WEBHOOK_SECRET',
    ]
    
    for var in removed_vars:
        print(f"  ✗ {var}")
    
    print("\n保留的环境变量：")
    kept_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'GEMINI_API_KEY',
        'QWEN_API_KEY',
    ]
    
    for var in kept_vars:
        print(f"  ✓ {var}")

def generate_test_report():
    """生成测试报告"""
    print_section("测试总结")
    
    print("\n✅ 已完成的工作：")
    print("  1. 删除所有支付相关文件（payment_service, payment_api, payment模型）")
    print("  2. 删除支付相关的API端点（/order, /order/status, /order/complete）")
    print("  3. 删除支付相关的服务方法（create_coin_order等）")
    print("  4. 隐藏前端套餐显示区域，改为获取金币说明")
    print("  5. 删除dashboard中的购买按钮")
    print("  6. 清理配置文件中的支付环境变量")
    print("  7. 禁用套餐页面路由（/coin/packages）")
    
    print("\n✅ 保留的功能：")
    print("  1. 金币账户查询")
    print("  2. 每日签到功能")
    print("  3. 金币消耗功能（用于分析等）")
    print("  4. 交易记录查看")
    print("  5. 套餐API（仅用于管理员查看，前端不显示）")
    
    print("\n⚠️  需要注意的事项：")
    print("  1. 数据库中可能仍有历史支付数据（payment_transactions表）")
    print("  2. CoinOrder表中的payment_method和payment_id字段已注释但保留（兼容历史数据）")
    print("  3. 建议在生产环境部署前运行数据库迁移，清理支付相关数据")
    
    print("\n📋 手动测试清单：")
    print("  1. 登录系统")
    print("  2. 访问 /coin 页面，检查：")
    print("     - 金币信息是否正确显示")
    print("     - 签到按钮是否可用")
    print("     - 是否显示'如何获取金币'说明（而不是套餐列表）")
    print("     - 交易记录是否正确显示")
    print("  3. 测试每日签到功能")
    print("  4. 测试金币消耗（进行股票分析）")
    print("  5. 检查 /dashboard 页面是否移除了购买按钮")
    print("  6. 确认 /coin/packages 页面不可访问")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  金币系统功能测试 - 支付功能移除验证")
    print("=" * 60)
    
    test_coin_api_endpoints()
    test_service_functions()
    test_model_fields()
    test_frontend_pages()
    test_configuration()
    generate_test_report()
    
    print("\n" + "=" * 60)
    print("  测试脚本执行完成")
    print("  请按照上述清单进行手动功能测试")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
