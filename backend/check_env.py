#!/usr/bin/env python3
"""
检查当前生效的环境变量配置
"""
import os
from dotenv import load_dotenv

def check_env():
    """检查环境变量配置"""
    print("🔍 检查环境变量配置...")
    print("=" * 50)
    
    # 检查.env文件是否存在
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ 找到.env文件: {os.path.abspath(env_file)}")
        
        # 读取.env文件内容
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        print(f"\n📄 .env文件内容:")
        print("-" * 30)
        for line in env_content.split('\n'):
            if line.strip() and not line.startswith('#'):
                if 'API_KEY' in line:
                    # 隐藏API密钥的敏感部分
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if value.strip() and value.strip() != 'your-deepseek-api-key-here':
                            # 显示前10个字符和后5个字符
                            masked_value = value.strip()[:10] + '...' + value.strip()[-5:]
                            print(f"  {key}={masked_value}")
                        else:
                            print(f"  {key}=[未配置]")
                    else:
                        print(f"  {line}")
                else:
                    print(f"  {line}")
    else:
        print(f"❌ 未找到.env文件")
    
    print("\n" + "=" * 50)
    print("🌍 当前系统环境变量:")
    print("-" * 30)
    
    # 检查关键环境变量
    key_vars = [
        'DEEPSEEK_API_KEY',
        'GEMINI_API_KEY', 
        'OPENAI_API_KEY',
        'QWEN_API_KEY',
        'DEFAULT_AI_PROVIDER'
    ]
    
    for var in key_vars:
        value = os.getenv(var)
        if value:
            if 'API_KEY' in var and len(value) > 15:
                # 隐藏API密钥的敏感部分
                masked_value = value[:10] + '...' + value[-5:]
                print(f"  {var}: {masked_value}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: [未设置]")
    
    print("\n" + "=" * 50)
    print("📋 环境变量加载测试:")
    print("-" * 30)
    
    # 测试加载.env文件
    try:
        load_dotenv()
        print("✅ python-dotenv加载成功")
        
        # 重新检查关键变量
        print("\n🔍 加载.env后的环境变量:")
        for var in key_vars:
            value = os.getenv(var)
            if value:
                if 'API_KEY' in var and len(value) > 15:
                    masked_value = value[:10] + '...' + value[-5:]
                    print(f"  {var}: {masked_value}")
                else:
                    print(f"  {var}: {value}")
            else:
                print(f"  {var}: [未设置]")
                
    except Exception as e:
        print(f"❌ python-dotenv加载失败: {e}")

if __name__ == "__main__":
    check_env()
