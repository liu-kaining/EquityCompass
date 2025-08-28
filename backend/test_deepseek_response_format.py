#!/usr/bin/env python3
"""
测试 DeepSeek API 响应格式
"""

import os
import json
import requests
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

def test_deepseek_response_format():
    """测试 DeepSeek API 响应格式"""
    
    # 加载环境变量
    load_env()
    
    # 获取配置
    api_key = os.getenv('DEEPSEEK_API_KEY')
    model = os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner')
    
    if not api_key:
        print("❌ 未找到 DEEPSEEK_API_KEY")
        return
    
    print(f"🔧 测试配置:")
    print(f"   模型: {model}")
    print(f"   API密钥长度: {len(api_key)}")
    print()
    
    # 测试1: 基础调用（无深度思考）
    print("=" * 60)
    print("🧪 测试1: 基础调用（无深度思考）")
    print("=" * 60)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data_basic = {
        "model": model,
        "messages": [
            {"role": "user", "content": "请简单介绍一下苹果公司"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data_basic,
            timeout=30
        )
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 基础调用成功")
            print(f"📝 响应结构: {list(result.keys())}")
            
            if 'choices' in result:
                choice = result['choices'][0]
                print(f"📋 Choice结构: {list(choice.keys())}")
                
                if 'message' in choice:
                    message = choice['message']
                    print(f"💬 Message结构: {list(message.keys())}")
                    print(f"📄 内容长度: {len(message.get('content', ''))} 字符")
                    print(f"📄 内容预览: {message.get('content', '')[:100]}...")
                else:
                    print(f"❌ Message字段不存在")
                    print(f"📋 Choice内容: {choice}")
            else:
                print(f"❌ Choices字段不存在")
                print(f"📋 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 基础调用异常: {str(e)}")
    
    print()
    
    # 测试2: 深度思考调用
    print("=" * 60)
    print("🧪 测试2: 深度思考调用")
    print("=" * 60)
    
    data_thinking = {
        "model": model,
        "messages": [
            {"role": "user", "content": "请深入分析苹果公司的投资价值"}
        ],
        "max_tokens": 200,
        "temperature": 0.7,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "reasoning",
                    "description": "启用推理模式",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "steps": {
                                "type": "integer",
                                "description": "推理步数",
                                "default": 3
                            }
                        }
                    }
                }
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data_thinking,
            timeout=30
        )
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 深度思考调用成功")
            print(f"📝 响应结构: {list(result.keys())}")
            
            if 'choices' in result:
                choice = result['choices'][0]
                print(f"📋 Choice结构: {list(choice.keys())}")
                
                if 'message' in choice:
                    message = choice['message']
                    print(f"💬 Message结构: {list(message.keys())}")
                    print(f"📄 内容长度: {len(message.get('content', ''))} 字符")
                    print(f"📄 内容预览: {message.get('content', '')[:100]}...")
                    
                    # 检查是否有 tool_calls
                    if 'tool_calls' in message:
                        print(f"🔧 发现 tool_calls: {len(message['tool_calls'])} 个")
                        for i, tool_call in enumerate(message['tool_calls']):
                            print(f"   工具调用 {i+1}: {tool_call}")
                else:
                    print(f"❌ Message字段不存在")
                    print(f"📋 Choice内容: {choice}")
            else:
                print(f"❌ Choices字段不存在")
                print(f"📋 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 深度思考调用异常: {str(e)}")
    
    print()
    print("🏁 测试完成")

if __name__ == "__main__":
    test_deepseek_response_format()
