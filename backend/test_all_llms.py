#!/usr/bin/env python3
"""
测试所有LLM提供商
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.ai.llm_provider import LLMProviderFactory

def test_all_providers():
    """测试所有LLM提供商"""
    print("🧪 测试所有LLM提供商...")
    
    app = create_app()
    
    with app.app_context():
        # 获取可用的提供商
        providers = LLMProviderFactory.get_available_providers()
        print(f"\n📋 可用提供商: {', '.join(providers)}")
        
        # 测试每个提供商
        for provider_type in providers:
            print(f"\n🔍 测试 {provider_type.upper()}...")
            
            # 获取配置
            if provider_type == 'gemini':
                config = {
                    'name': 'gemini',
                    'api_key': app.config.get('GEMINI_API_KEY'),
                    'model': app.config.get('GEMINI_MODEL', 'gemini-2.0-flash'),
                    'max_tokens': 100,
                    'temperature': 0.7
                }
            elif provider_type == 'chatgpt':
                config = {
                    'name': 'chatgpt',
                    'api_key': app.config.get('OPENAI_API_KEY'),
                    'model': app.config.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
                    'max_tokens': 100,
                    'temperature': 0.7
                }
            elif provider_type == 'qwen':
                config = {
                    'name': 'qwen',
                    'api_key': app.config.get('QWEN_API_KEY'),
                    'model': app.config.get('QWEN_MODEL', 'qwen-turbo'),
                    'max_tokens': 100,
                    'temperature': 0.7
                }
            elif provider_type == 'deepseek':
                config = {
                    'name': 'deepseek',
                    'api_key': app.config.get('DEEPSEEK_API_KEY'),
                    'model': app.config.get('DEEPSEEK_MODEL', 'deepseek-chat'),
                    'max_tokens': 100,
                    'temperature': 0.7
                }
            else:
                print(f"❌ 未知提供商: {provider_type}")
                continue
            
            # 检查API密钥
            if not config['api_key']:
                print(f"⚠️  {provider_type.upper()} API密钥未配置")
                continue
            
            try:
                # 创建提供商实例
                provider = LLMProviderFactory.create_provider(provider_type, config)
                
                # 测试连接
                print(f"  🔗 测试连接...")
                if provider.test_connection():
                    print(f"  ✅ {provider_type.upper()} 连接成功")
                    
                    # 测试简单分析
                    print(f"  📝 测试简单分析...")
                    stock_info = {
                        'code': 'AAPL',
                        'name': '苹果公司',
                        'market': 'US',
                        'industry': '消费电子',
                        'exchange': 'NASDAQ',
                        'analysis_date': '2025-01-01'
                    }
                    
                    result = provider.generate_analysis("请简单介绍一下 ${name} 公司", stock_info)
                    
                    if result['success']:
                        print(f"  ✅ {provider_type.upper()} 分析成功")
                        print(f"  📊 响应时间: {result.get('response_time', 0):.2f}秒")
                        print(f"  🎯 使用模型: {result.get('model', 'unknown')}")
                        print(f"  📝 内容预览: {result['content'][:100]}...")
                    else:
                        print(f"  ❌ {provider_type.upper()} 分析失败: {result.get('error', '未知错误')}")
                else:
                    print(f"  ❌ {provider_type.upper()} 连接失败")
                    
            except Exception as e:
                print(f"  ❌ {provider_type.upper()} 测试异常: {str(e)}")
        
        print("\n🎉 所有LLM提供商测试完成！")

def test_analysis_service():
    """测试分析服务"""
    print("\n🧪 测试分析服务...")
    
    app = create_app()
    
    with app.app_context():
        from app.services.ai.analysis_service import AnalysisService
        
        service = AnalysisService(db.session)
        
        # 获取默认提供商
        default_provider = app.config.get('DEFAULT_AI_PROVIDER', 'gemini')
        print(f"📋 默认AI提供商: {default_provider}")
        
        # 测试提示词
        print("\n📝 测试提示词:")
        for prompt_type in ['default', 'fundamental', 'technical']:
            prompt = service._get_analysis_prompt(prompt_type)
            print(f"  - {prompt_type}: {len(prompt)} 字符")

if __name__ == "__main__":
    test_all_providers()
    test_analysis_service()
