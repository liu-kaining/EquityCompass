#!/usr/bin/env python3
"""
测试提示词修复功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai.llm_provider import QwenProvider, DeepSeekProvider, GeminiProvider

def test_qwen_deep_research_prompt():
    """测试Qwen深度研究模型的提示词处理"""
    print("测试Qwen深度研究模型提示词处理...")
    
    # 创建测试配置
    config = {
        'name': 'qwen-test',
        'api_key': 'test-key',
        'model': 'qwen-deep-research',
        'max_tokens': 15000,
        'temperature': 0.7
    }
    
    try:
        provider = QwenProvider(config)
        
        # 测试用户提示词
        user_prompt = "请对股票AAPL进行技术分析，重点关注价格趋势和技术指标。"
        stock_info = {
            'code': 'AAPL',
            'name': 'Apple Inc.',
            'market': 'NASDAQ',
            'industry': 'Technology',
            'exchange': 'NASDAQ'
        }
        
        # 格式化提示词
        formatted_prompt = provider.format_prompt(user_prompt, stock_info)
        
        # 验证提示词没有被覆盖
        assert "请对股票AAPL进行技术分析" in formatted_prompt
        assert "重点关注价格趋势和技术指标" in formatted_prompt
        
        # 验证没有硬编码的研究提示词
        assert "研究目标：生成一份机构级别的专业投资分析报告" not in formatted_prompt
        assert "分析维度：" not in formatted_prompt
        
        print("✓ Qwen深度研究模型提示词处理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ Qwen深度研究模型测试失败: {str(e)}")
        return False

def test_deepseek_prompt():
    """测试DeepSeek的提示词处理"""
    print("测试DeepSeek提示词处理...")
    
    # 创建测试配置
    config = {
        'name': 'deepseek-test',
        'api_key': 'test-key',
        'model': 'deepseek-chat',
        'max_tokens': 15000,
        'temperature': 0.7,
        'enable_deep_thinking': True
    }
    
    try:
        provider = DeepSeekProvider(config)
        
        # 测试用户提示词
        user_prompt = "请对股票MSFT进行基本面分析，重点关注财务数据和估值。"
        stock_info = {
            'code': 'MSFT',
            'name': 'Microsoft Corporation',
            'market': 'NASDAQ',
            'industry': 'Technology',
            'exchange': 'NASDAQ'
        }
        
        # 格式化提示词
        formatted_prompt = provider.format_prompt(user_prompt, stock_info)
        
        # 验证提示词没有被覆盖
        assert "请对股票MSFT进行基本面分析" in formatted_prompt
        assert "重点关注财务数据和估值" in formatted_prompt
        
        print("✓ DeepSeek提示词处理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek测试失败: {str(e)}")
        return False

def test_gemini_prompt():
    """测试Gemini的提示词处理"""
    print("测试Gemini提示词处理...")
    
    # 创建测试配置
    config = {
        'name': 'gemini-test',
        'api_key': 'test-key',
        'model': 'gemini-2.0-flash',
        'max_tokens': 15000,
        'temperature': 0.7
    }
    
    try:
        provider = GeminiProvider(config)
        
        # 测试用户提示词
        user_prompt = "请对股票GOOGL进行综合分析，包括技术面和基本面。"
        stock_info = {
            'code': 'GOOGL',
            'name': 'Alphabet Inc.',
            'market': 'NASDAQ',
            'industry': 'Technology',
            'exchange': 'NASDAQ'
        }
        
        # 格式化提示词
        formatted_prompt = provider.format_prompt(user_prompt, stock_info)
        
        # 验证提示词没有被覆盖
        assert "请对股票GOOGL进行综合分析" in formatted_prompt
        assert "包括技术面和基本面" in formatted_prompt
        
        print("✓ Gemini提示词处理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ Gemini测试失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("开始测试提示词修复功能...\n")
    
    tests = [
        test_qwen_deep_research_prompt,
        test_deepseek_prompt,
        test_gemini_prompt
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！提示词修复功能正常工作。")
        return True
    else:
        print("❌ 部分测试失败，请检查修复。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
