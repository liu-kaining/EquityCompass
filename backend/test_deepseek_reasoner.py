#!/usr/bin/env python3
"""
测试 DeepSeek Reasoner 模型
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

def test_deepseek_reasoner():
    """测试 DeepSeek Reasoner 模型"""
    
    # 加载环境变量
    load_env()
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ 请设置 DEEPSEEK_API_KEY 环境变量")
        return False
    
    print(f"🔑 API密钥: {api_key[:10]}...")
    
    # 测试不同的模型
    models = ['deepseek-reasoner', 'deepseek-coder', 'deepseek-chat']
    
    for model in models:
        print(f"\n🧪 测试模型: {model}")
        
        try:
            # 准备请求
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            # 基础请求数据
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的股票分析师。"},
                    {"role": "user", "content": "请简要分析一下股票投资的基本要素。"}
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            # 如果是 reasoner 模型，使用内置推理能力
            if model == 'deepseek-reasoner':
                data["messages"][0]["content"] = "你是一个专业的股票分析师，请根据提供的信息进行专业的股票分析。请深入思考，进行多步推理，提供详细的分析和投资建议。"
                print("🔧 使用 DeepSeek Reasoner 内置推理能力")
            
            print(f"📤 发送请求到 {url}")
            print(f"📋 请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 发送请求
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {model} 模型测试成功")
                
                # 显示响应内容
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
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

if __name__ == "__main__":
    print("🚀 开始测试 DeepSeek 模型...")
    success = test_deepseek_reasoner()
    
    if success:
        print("\n🎉 测试完成！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)
