#!/usr/bin/env python3
"""
测试 DeepSeek 工具调用流程
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

def test_deepseek_tool_calls():
    """测试 DeepSeek 工具调用流程"""
    
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
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    # 第一步：发送带有工具调用的请求
    print("=" * 60)
    print("🧪 第一步：发送带有工具调用的请求")
    print("=" * 60)
    
    data = {
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
            json=data,
            timeout=30
        )
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 第一步请求成功")
            
            # 检查是否有工具调用
            message = result['choices'][0]['message']
            print(f"📋 Message结构: {list(message.keys())}")
            
            if 'tool_calls' in message and message['tool_calls']:
                print(f"🔧 发现工具调用: {len(message['tool_calls'])} 个")
                
                # 第二步：处理工具调用
                print()
                print("=" * 60)
                print("🧪 第二步：处理工具调用")
                print("=" * 60)
                
                # 构建后续请求
                follow_up_data = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "请深入分析苹果公司的投资价值"},
                        message  # 包含工具调用的消息
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                
                print("📤 发送后续请求...")
                follow_up_response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=follow_up_data,
                    timeout=60
                )
                
                print(f"📡 后续响应状态码: {follow_up_response.status_code}")
                
                if follow_up_response.status_code == 200:
                    follow_up_result = follow_up_response.json()
                    print(f"✅ 后续请求成功")
                    
                    follow_up_message = follow_up_result['choices'][0]['message']
                    print(f"📋 后续Message结构: {list(follow_up_message.keys())}")
                    
                    if 'content' in follow_up_message:
                        content = follow_up_message['content']
                        print(f"📄 最终内容长度: {len(content)} 字符")
                        print(f"📄 内容预览: {content[:200]}...")
                    else:
                        print(f"❌ 后续响应中没有content字段")
                        print(f"📋 完整响应: {json.dumps(follow_up_result, indent=2, ensure_ascii=False)}")
                else:
                    print(f"❌ 后续请求失败: {follow_up_response.text}")
            else:
                print(f"❌ 没有发现工具调用")
                print(f"📋 Message内容: {message}")
        else:
            print(f"❌ 第一步请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
    
    print()
    print("🏁 测试完成")

if __name__ == "__main__":
    test_deepseek_tool_calls()
