#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI分析功能测试
验证各种LLM提供商的分析功能
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.ai.analysis_service import AnalysisService
from app.services.ai.llm_provider import LLMProvider

def test_ai_analysis():
    """测试AI分析功能"""
    print("🧪 测试AI分析功能...")
    
    app = create_app()
    with app.app_context():
        from app import db
        analysis_service = AnalysisService(db.session)
        
        # 测试股票信息
        test_stock = {
            'code': 'AAPL',
            'name': '苹果公司',
            'market': 'US',
            'industry': '科技'
        }
        
        print(f"\n📊 测试股票: {test_stock['code']} - {test_stock['name']}")
        
        # 测试所有可用的LLM提供商
        providers = ['gemini', 'qwen', 'deepseek']
        
        for provider_name in providers:
            print(f"\n🔍 测试 {provider_name.upper()}...")
            
            try:
                # 测试连接
                print(f"  🔗 测试连接...")
                from app.services.ai.llm_provider import LLMProviderFactory
                
                # 配置测试
                if provider_name == 'gemini':
                    provider_config = {
                        'name': 'gemini',
                        'api_key': os.getenv('GEMINI_API_KEY'),
                        'model': 'gemini-2.0-flash'
                    }
                elif provider_name == 'qwen':
                    provider_config = {
                        'name': 'qwen',
                        'api_key': os.getenv('QWEN_API_KEY'),
                        'model': 'qwen-plus'
                    }
                elif provider_name == 'deepseek':
                    provider_config = {
                        'name': 'deepseek',
                        'api_key': os.getenv('DEEPSEEK_API_KEY'),
                        'model': 'deepseek-chat'
                    }
                else:
                    print(f"  ❌ 不支持的提供商: {provider_name}")
                    continue
                
                if not provider_config['api_key']:
                    print(f"  ⚠️  {provider_name.upper()} API密钥未配置")
                    continue
                
                provider = LLMProviderFactory.create_provider(provider_name, provider_config)
                
                # 测试连接
                if not provider.test_connection():
                    print(f"  ❌ {provider_name.upper()} 连接失败")
                    continue
                
                print(f"  ✅ {provider_name.upper()} 连接成功")
                
                # 测试简单分析
                print(f"  📝 测试简单分析...")
                start_time = time.time()
                
                prompt = f"请简要介绍一下{test_stock['name']}（{test_stock['code']}）这家公司。"
                result = provider.generate_analysis(prompt, test_stock)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if result['success'] and result.get('content'):
                    print(f"  ✅ {provider_name.upper()} 分析成功")
                    print(f"  📊 响应时间: {response_time:.2f}秒")
                    print(f"  🎯 使用模型: {result.get('model', 'unknown')}")
                    
                    # 显示内容预览
                    content = result.get('content', '')
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"  📝 内容预览: {preview}")
                else:
                    error_msg = result.get('error', '无响应')
                    print(f"  ❌ {provider_name.upper()} 分析失败: {error_msg}")
                    
            except Exception as e:
                print(f"  ❌ {provider_name.upper()} 测试异常: {str(e)}")
        
        # 测试分析服务
        print(f"\n🧪 测试分析服务...")
        print(f"📋 默认AI提供商: gemini")
        
        # 测试提示词
        try:
            prompts = analysis_service._get_analysis_prompt()
            print(f"  - 默认提示词: {len(prompts)} 字符")
        except Exception as e:
            print(f"  - 提示词获取失败: {e}")
        
        print(f"\n🎉 AI分析功能测试完成！")

if __name__ == "__main__":
    test_ai_analysis()
