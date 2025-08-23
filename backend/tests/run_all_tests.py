#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有测试
统一执行所有功能测试
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行所有测试...")
    print("=" * 50)
    
    start_time = time.time()
    
    # 测试列表
    tests = [
        ("环境配置测试", "test_environment.py"),
        ("股票数据测试", "test_stock_data.py"),
        ("关注列表测试", "test_watchlist.py"),
        ("AI分析测试", "test_ai_analysis.py"),
        ("仪表板统计测试", "test_dashboard_stats.py")
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_file in tests:
        print(f"\n🧪 运行 {test_name}...")
        print("-" * 30)
        
        try:
            # 导入并运行测试
            test_module = __import__(f"tests.{test_file[:-3]}", fromlist=['*'])
            
            # 查找测试函数
            test_functions = [attr for attr in dir(test_module) if attr.startswith('test_')]
            
            for func_name in test_functions:
                test_func = getattr(test_module, func_name)
                if callable(test_func):
                    test_func()
            
            print(f"✅ {test_name} 完成")
            passed += 1
            
        except Exception as e:
            print(f"❌ {test_name} 失败: {e}")
            failed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"   总测试数: {len(tests)}")
    print(f"   通过: {passed}")
    print(f"   失败: {failed}")
    print(f"   总耗时: {total_time:.2f}秒")
    
    if failed == 0:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️  有 {failed} 个测试失败，请检查相关功能")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
