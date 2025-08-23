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
        providers = ['gemini', 'qwen', 'deepseek', 'chatgpt']
        
        for provider_name in providers:
            print(f"\n🔍 测试 {provider_name.upper()}...")
            
            try:
                # 测试连接
                print(f"  🔗 测试连接...")
                provider = LLMProvider(provider_name)
                
                if not provider.is_available():
                    print(f"  ❌ {provider_name.upper()} 不可用")
                    continue
                
                print(f"  ✅ {provider_name.upper()} 连接成功")
                
                # 测试简单分析
                print(f"  📝 测试简单分析...")
                start_time = time.time()
                
                prompt = f"请简要介绍一下{test_stock['name']}（{test_stock['code']}）这家公司。"
                response = provider.analyze(prompt)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response and response.strip():
                    print(f"  ✅ {provider_name.upper()} 分析成功")
                    print(f"  📊 响应时间: {response_time:.2f}秒")
                    print(f"  🎯 使用模型: {provider.get_model_name()}")
                    
                    # 显示内容预览
                    preview = response[:200] + "..." if len(response) > 200 else response
                    print(f"  📝 内容预览: {preview}")
                else:
                    print(f"  ❌ {provider_name.upper()} 分析失败: 无响应")
                    
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
