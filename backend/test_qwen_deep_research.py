#!/usr/bin/env python3
"""
测试 qwen-deep-research 模型
"""

import os
import sys
import json
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

def test_qwen_deep_research():
    """测试 qwen-deep-research 模型"""
    
    # 加载环境变量
    load_env()
    
    api_key = os.getenv('QWEN_API_KEY')
    if not api_key:
        print("❌ 请设置 QWEN_API_KEY 环境变量")
        return False
    
    print(f"🔑 API密钥: {api_key[:10]}...")
    
    try:
        import dashscope
        from dashscope import Generation
        
        # 设置API Key
        dashscope.api_key = api_key
        
        print(f"\n🧪 测试模型: qwen-deep-research")
        
        # 准备请求
        research_prompt = "请深入研究并分析苹果公司(AAPL)的投资价值，包括基本面分析、技术面分析和投资建议。"
        
        api_params = {
            'model': 'qwen-deep-research',
            'messages': [{'role': 'user', 'content': research_prompt}],
            'stream': True  # qwen-deep-research 目前仅支持流式输出
        }
        
        print(f"📤 发送请求到 qwen-deep-research")
        print(f"📋 研究提示: {research_prompt}")
        
        # 调用流式API
        responses = Generation.call(**api_params)
        
        current_phase = None
        phase_content = ""
        final_content = ""
        research_goal = ""
        web_sites = []
        
        print(f"📥 开始接收流式响应...")
        
        for response in responses:
            # 检查响应状态码
            if hasattr(response, 'status_code') and response.status_code != 200:
                print(f"❌ HTTP返回码：{response.status_code}")
                if hasattr(response, 'code'):
                    print(f"错误码：{response.code}")
                if hasattr(response, 'message'):
                    print(f"错误信息：{response.message}")
                continue
            
            if hasattr(response, 'output') and response.output:
                message = response.output.get('message', {})
                phase = message.get('phase')
                content = message.get('content', '')
                status = message.get('status')
                extra = message.get('extra', {})
                
                # 阶段变化检测
                if phase != current_phase:
                    if current_phase and phase_content:
                        print(f"✅ {current_phase} 阶段完成")
                    current_phase = phase
                    phase_content = ""
                    print(f"🔄 进入 {phase} 阶段")
                
                # 累积阶段内容
                if content:
                    phase_content += content
                    final_content += content
                    print(f"📝 内容更新: {len(content)} 字符")
                
                # 处理WebResearch阶段的特殊信息
                if phase == "WebResearch":
                    if extra.get('deep_research', {}).get('research'):
                        research_info = extra['deep_research']['research']
                        
                        # 处理streamingQueries状态
                        if status == "streamingQueries":
                            if 'researchGoal' in research_info:
                                goal = research_info['researchGoal']
                                if goal and goal != research_goal:
                                    research_goal = goal
                                    print(f"🎯 研究目标: {goal}")
                        
                        # 处理streamingWebResult状态
                        elif status == "streamingWebResult":
                            if 'webSites' in research_info:
                                sites = research_info['webSites']
                                if sites and len(sites) > len(web_sites):
                                    web_sites = sites
                                    print(f"🌐 发现 {len(sites)} 个网站")
                                    for i, site in enumerate(sites):
                                        print(f"   {i+1}. {site.get('title', 'N/A')} - {site.get('url', 'N/A')}")
                
                # 检查是否完成
                if status == "finished" and phase == "answer":
                    print(f"✅ 最终报告生成完成")
                    break
        
        # 如果没有获取到内容，使用阶段内容
        if not final_content and phase_content:
            final_content = phase_content
        
        print(f"\n📊 测试结果:")
        print(f"   最终内容长度: {len(final_content)} 字符")
        if final_content:
            print(f"   内容预览: {final_content[:200]}...")
        if research_goal:
            print(f"   研究目标: {research_goal}")
        if web_sites:
            print(f"   搜索网站数: {len(web_sites)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试 qwen-deep-research 模型...")
    success = test_qwen_deep_research()
    
    if success:
        print("\n🎉 测试完成！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)
