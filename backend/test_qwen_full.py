#!/usr/bin/env python3
"""
测试 qwen-deep-research 完整流程
"""

import os
import sys
from datetime import datetime

def load_env():
    """加载环境变量"""
    env_file = '../.env'
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def test_qwen_full():
    """测试 qwen-deep-research 完整流程"""
    
    load_env()
    api_key = os.getenv('QWEN_API_KEY')
    if not api_key:
        print("❌ 请设置 QWEN_API_KEY")
        return False
    
    try:
        import dashscope
        from dashscope import Generation
        dashscope.api_key = api_key
        
        print("🧪 测试 qwen-deep-research 完整流程")
        
        # 初始请求
        initial_prompt = "请对苹果公司(AAPL)进行深入的投资分析，生成详细的专业报告。"
        
        api_params = {
            'model': 'qwen-deep-research',
            'messages': [{'role': 'user', 'content': initial_prompt}],
            'stream': True,
            'parameters': {'max_tokens': 15000, 'temperature': 0.7}
        }
        
        print("📤 发送初始请求...")
        responses = Generation.call(**api_params)
        
        confirmation_questions = ""
        final_content = ""
        
        for response in responses:
            if hasattr(response, 'status_code') and response.status_code != 200:
                continue
                
            if hasattr(response, 'output') and response.output:
                message = response.output.get('message', {})
                phase = message.get('phase')
                content = message.get('content', '')
                status = message.get('status')
                
                if content:
                    if phase == "answer" and status == "typing":
                        confirmation_questions += content
                    else:
                        final_content += content
                
                if status == "finished" and phase == "answer":
                    break
        
        print(f"📊 结果:")
        print(f"   反问问题长度: {len(confirmation_questions)} 字符")
        print(f"   最终内容长度: {len(final_content)} 字符")
        
        if confirmation_questions:
            print(f"   反问问题: {confirmation_questions[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试...")
    success = test_qwen_full()
    print("🎉 完成！" if success else "❌ 失败！")
