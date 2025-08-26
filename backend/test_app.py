#!/usr/bin/env python3
"""
测试app模块是否可以正确导入
"""
import os
import sys

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')

print("开始测试app模块导入...")

try:
    # 测试导入create_app
    from app import create_app
    print("✅ create_app导入成功")
    
    # 测试创建应用
    app = create_app()
    print("✅ 应用创建成功")
    
    # 测试app对象
    print(f"✅ app对象类型: {type(app)}")
    
    print("🎉 所有测试通过！")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
