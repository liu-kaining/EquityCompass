#!/usr/bin/env python3
"""
测试 Qwen 不同模型和功能
"""
import os
import sys
import requests
import json

# 从 .env 文件加载环境变量
def load_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def test_qwen_models():
    """测试 Qwen 不同模型"""
    
    # 加载环境变量
    load_env()
    
    api_key = os.getenv('QWEN_API_KEY')
    if not api_key:
        print("❌ 请设置 QWEN_API_KEY 环境变量")
        return False
    
    print(f"🔑 API密钥: {api_key[:10]}...")
    
    # 测试不同的模型
    models = ['qwen-max', 'qwen-plus', 'qwen-turbo']
    
    for model in models:
        print(f"\n🧪 测试模型: {model}")
        
        try:
            # 准备请求
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            # 基础请求数据
            data = {
                "model": model,
                "input": {
                    "messages": [
                        {"role": "system", "content": "你是一个专业的股票分析师。"},
                        {"role": "user", "content": "请简要分析一下股票投资的基本要素。"}
                    ]
                },
                "parameters": {
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "result_format": "message"
                }
            }
            
            print(f"📤 发送请求到 {url}")
            print(f"📋 请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {model} 模型测试成功")
                
                # 显示响应内容
                if 'output' in result and 'choices' in result['output']:
                    content = result['output']['choices'][0]['message']['content']
                    print(f"📝 响应内容预览: {content[:200]}...")
                
                # 显示使用情况
                if 'usage' in result:
                    usage = result['usage']
                    print(f"📊 Token使用: {usage}")
                
                return True
            else:
                print(f"❌ {model} 模型测试失败")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ {model} 模型测试出错: {str(e)}")
    
    return False

def test_qwen_tools():
    """测试 Qwen 工具功能"""
    
    api_key = os.getenv('QWEN_API_KEY')
    if not api_key:
        print("❌ 请设置 QWEN_API_KEY 环境变量")
        return False
    
    print(f"\n🔧 测试 Qwen 工具功能...")
    
    try:
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # 测试带工具的请求
        data = {
            "model": "qwen-max",
            "input": {
                "messages": [
                    {"role": "system", "content": "你是一个专业的股票分析师。"},
                    {"role": "user", "content": "请分析平安银行的最新情况。"}
                ]
            },
            "parameters": {
                "max_tokens": 1000,
                "temperature": 0.7,
                "result_format": "message",
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "description": "搜索最新信息",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "搜索查询"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        print(f"📤 发送带工具的请求...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 工具功能测试成功")
            return True
        else:
            print(f"❌ 工具功能测试失败")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 工具功能测试出错: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试 Qwen 模型和功能...")
    
    # 测试不同模型
    models_success = test_qwen_models()
    
    # 测试工具功能
    tools_success = test_qwen_tools()
    
    if models_success and tools_success:
        print("\n🎉 所有测试完成！")
    else:
        print("\n❌ 部分测试失败！")
        sys.exit(1)
