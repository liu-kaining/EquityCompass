#!/usr/bin/env python3
"""
测试 qwen-deep-research 完整流程（包括自动回答反问）
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

def test_qwen_complete():
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
        
        print("🧪 测试 qwen-deep-research 完整流程（包括自动回答反问）")
        
        # 第一步：获取反问确认问题
        print("\n📤 第一步：获取反问确认问题")
        initial_prompt = "请对苹果公司(AAPL)进行深入的投资分析，生成详细的专业报告。"
        
        api_params = {
            'model': 'qwen-deep-research',
            'messages': [{'role': 'user', 'content': initial_prompt}],
            'stream': True,
            'parameters': {'max_tokens': 15000, 'temperature': 0.7}
        }
        
        responses = Generation.call(**api_params)
        
        confirmation_questions = ""
        
        for response in responses:
            if hasattr(response, 'status_code') and response.status_code != 200:
                continue
                
            if hasattr(response, 'output') and response.output:
                message = response.output.get('message', {})
                phase = message.get('phase')
                content = message.get('content', '')
                status = message.get('status')
                
                if content and phase == "answer" and status == "typing":
                    confirmation_questions += content
                
                if status == "finished" and phase == "answer":
                    break
        
        print(f"✅ 反问问题获取完成，长度: {len(confirmation_questions)} 字符")
        
        # 第二步：自动回答反问问题并继续分析
        if confirmation_questions:
            print("\n📤 第二步：自动回答反问问题并继续分析")
            
            # 构建自动回答
            auto_response = """基于您的分析需求，我提供以下确认信息：

1. 投资时间框架：我希望分析涵盖短期（6个月）、中期（1-2年）和长期（3-5年）三个时间维度，重点关注中长期投资价值，但也要包含短期交易机会的识别。

2. 财务分析重点：请重点分析自由现金流折现（DCF）、ROIC趋势、毛利率和净利率变化、资本回报率等关键指标，同时包含相对估值法（P/E、P/S、EV/EBITDA）的对比分析。

3. 行业分析范围：请深入分析公司与主要竞争对手在生态系统、技术创新、市场份额等方面的对比，特别关注公司在高端市场的护城河效应。

4. 技术面分析：请结合短期技术指标（支撑阻力、动量指标）和长期趋势结构（周线级别波浪理论、机构持仓变化）进行多维度分析。

5. 风险因素：请重点关注供应链风险、监管风险、技术颠覆风险、地缘政治风险等关键不确定性因素。

请基于以上确认信息，生成一份极其详细、专业的投资分析报告。"""
            
            # 构建完整对话
            full_conversation = [
                {'role': 'user', 'content': initial_prompt},
                {'role': 'assistant', 'content': confirmation_questions},
                {'role': 'user', 'content': auto_response}
            ]
            
            # 发送包含自动回答的请求
            follow_up_params = {
                'model': 'qwen-deep-research',
                'messages': full_conversation,
                'stream': True,
                'parameters': {'max_tokens': 15000, 'temperature': 0.7}
            }
            
            follow_up_responses = Generation.call(**follow_up_params)
            
            final_content = ""
            research_goal = ""
            web_sites = []
            
            for response in follow_up_responses:
                if hasattr(response, 'status_code') and response.status_code != 200:
                    continue
                
                if hasattr(response, 'output') and response.output:
                    message = response.output.get('message', {})
                    phase = message.get('phase')
                    content = message.get('content', '')
                    status = message.get('status')
                    extra = message.get('extra', {})
                    
                    if content:
                        final_content += content
                        print(f"📝 内容更新: {len(content)} 字符 (累计: {len(final_content)} 字符)")
                    
                    # 处理WebResearch阶段的特殊信息
                    if phase == "WebResearch":
                        if extra.get('deep_research', {}).get('research'):
                            research_info = extra['deep_research']['research']
                            
                            if status == "streamingQueries":
                                if 'researchGoal' in research_info:
                                    goal = research_info['researchGoal']
                                    if goal and goal != research_goal:
                                        research_goal = goal
                                        print(f"🎯 研究目标: {goal}")
                            
                            elif status == "streamingWebResult":
                                if 'webSites' in research_info:
                                    sites = research_info['webSites']
                                    if sites and len(sites) > len(web_sites):
                                        web_sites = sites
                                        print(f"🌐 发现 {len(sites)} 个网站")
                    
                    if status == "finished" and phase == "answer":
                        print("✅ 最终报告生成完成")
                        break
            
            # 构建完整报告
            complete_report = f"""# 苹果公司 (AAPL) 专业投资分析报告

## 分析确认问题

{confirmation_questions}

## 详细分析报告

{final_content}"""
            
            print(f"\n📊 最终结果:")
            print(f"   完整报告长度: {len(complete_report)} 字符")
            print(f"   反问问题长度: {len(confirmation_questions)} 字符")
            print(f"   详细报告长度: {len(final_content)} 字符")
            print(f"   内容长度是否符合要求: {'✅ 是' if len(complete_report) >= 3000 else '❌ 否'}")
            
            if complete_report:
                print(f"   完整报告预览: {complete_report[:300]}...")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试完整流程...")
    success = test_qwen_complete()
    print("🎉 完成！" if success else "❌ 失败！")
