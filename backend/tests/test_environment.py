#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境配置测试
验证环境变量和配置是否正确
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config import Config

def test_environment():
    """测试环境配置"""
    print("=== 环境配置测试 ===")
    
    # 测试Flask应用创建
    print("🔧 测试Flask应用创建...")
    try:
        app = create_app()
        print("   ✅ Flask应用创建成功")
    except Exception as e:
        print(f"   ❌ Flask应用创建失败: {e}")
        return
    
    # 测试配置
    print(f"\n⚙️  应用配置:")
    print(f"   调试模式: {app.config.get('DEBUG', 'Unknown')}")
    print(f"   测试模式: {app.config.get('TESTING', 'Unknown')}")
    print(f"   数据库URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')[:50]}...")
    
    # 测试环境变量
    print(f"\n🌍 环境变量检查:")
    env_vars = [
        'FLASK_ENV',
        'SECRET_KEY',
        'GEMINI_API_KEY',
        'OPENAI_API_KEY',
        'QWEN_API_KEY',
        'DEEPSEEK_API_KEY'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if 'API_KEY' in var:
                display_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ⚠️  {var}: 未设置")
    
    # 测试数据库连接
    print(f"\n🗄️  数据库连接测试...")
    try:
        with app.app_context():
            from app import db
            # 尝试执行简单查询
            result = db.session.execute('SELECT 1').fetchone()
            print("   ✅ 数据库连接成功")
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
    
    # 测试AI服务配置
    print(f"\n🤖 AI服务配置:")
    try:
        from app.services.ai.analysis_service import AnalysisService
        analysis_service = AnalysisService()
        default_provider = analysis_service.get_default_provider()
        print(f"   默认AI提供商: {default_provider}")
        
        # 检查提供商可用性
        providers = ['gemini', 'qwen', 'deepseek', 'chatgpt']
        for provider in providers:
            try:
                from app.services.ai.llm_provider import LLMProvider
                llm = LLMProvider(provider)
                if llm.is_available():
                    print(f"   ✅ {provider.upper()}: 可用")
                else:
                    print(f"   ⚠️  {provider.upper()}: 不可用")
            except Exception as e:
                print(f"   ❌ {provider.upper()}: 配置错误 - {str(e)[:50]}")
                
    except Exception as e:
        print(f"   ❌ AI服务配置检查失败: {e}")
    
    print(f"\n✅ 环境配置测试完成！")

if __name__ == "__main__":
    test_environment()
