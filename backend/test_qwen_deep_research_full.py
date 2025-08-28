#!/usr/bin/env python3
"""
测试 qwen-deep-research 完整流程（包括反问确认）
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

def test_qwen_deep_research_full():
    """测试 qwen-deep-research 完整流程"""
    
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
        
        print(f"\n🧪 测试 qwen-deep-research 完整流程")
        
        # 第一步：发送初始分析请求
        print("=" * 60)
        print("📤 第一步：发送初始分析请求")
        print("=" * 60)
        
        initial_prompt = """请对股票 苹果公司 (AAPL) 进行极其深入、详细、专业的投资分析。

研究目标：生成一份机构级别的专业投资分析报告，内容必须非常详细（至少3000-5000字），包含大量具体数据、专业术语和深度分析。

分析维度：
1. 公司概况与商业模式深度分析
2. 财务健康度与盈利能力量化评估
3. 行业地位与竞争优势分析
4. 技术面分析与市场情绪评估
5. 风险评估与不确定性分析
6. 投资建议与操作策略
7. 风险提示与免责声明

分析要求：
- 使用专业的金融分析框架和方法论
- 包含定量分析和定性分析
- 提供具体的投资建议和操作策略
- 使用大量专业术语和数据支撑
- 报告结构清晰，逻辑严密

请基于以下信息进行深入分析：
请对苹果公司(AAPL)进行全面的基本面分析，包括公司概况、财务分析、行业分析、风险评估和投资建议。

请在反问确认阶段就提供详细的分析框架和关键问题，然后在研究阶段生成极其详细、专业的投资分析报告。"""
        
        api_params = {
            'model': 'qwen-deep-research',
            'messages': [{'role': 'user', 'content': initial_prompt}],
            'stream': True,
            'parameters': {
                'max_tokens': 15000,
                'temperature': 0.7
            }
        }
        
        print(f"📋 初始提示词长度: {len(initial_prompt)} 字符")
        
        # 调用流式API
        responses = Generation.call(**api_params)
        
        current_phase = None
        phase_content = ""
        confirmation_questions = ""
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
                    
                    # 如果是反问确认阶段，记录问题
                    if phase == "answer" and status == "typing":
                        confirmation_questions += content
                        print(f"📝 反问问题更新: {len(content)} 字符 (累计: {len(confirmation_questions)} 字符)")
                
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
                
                # 检查是否完成
                if status == "finished" and phase == "answer":
                    print(f"✅ 最终报告生成完成")
                    break
        
        print(f"\n📊 第一步结果:")
        print(f"   反问问题长度: {len(confirmation_questions)} 字符")
        if confirmation_questions:
            print(f"   反问问题预览: {confirmation_questions[:200]}...")
        
        # 第二步：模拟用户回答反问问题
        print("\n" + "=" * 60)
        print("📤 第二步：模拟用户回答反问问题")
        print("=" * 60)
        
        # 构建用户回答
        user_response = """基于您的分析需求，我提供以下确认信息：

1. 投资时间框架：我希望分析涵盖短期（6个月）、中期（1-2年）和长期（3-5年）三个时间维度，重点关注中长期投资价值，但也要包含短期交易机会的识别。

2. 财务分析重点：请重点分析自由现金流折现（DCF）、ROIC趋势、毛利率和净利率变化、资本回报率等关键指标，同时包含相对估值法（P/E、P/S、EV/EBITDA）的对比分析。

3. 行业分析范围：请深入分析苹果与主要竞争对手（微软、谷歌、三星、华为等）在生态系统、硬件创新、服务收入增长、市场份额等方面的对比，特别关注苹果在高端市场的护城河效应。

4. 技术面分析：请结合短期技术指标（支撑阻力、动量指标）和长期趋势结构（周线级别波浪理论、机构持仓变化）进行多维度分析。

5. 风险因素：请重点关注供应链风险、监管风险、技术颠覆风险、地缘政治风险等关键不确定性因素。

请基于以上确认信息，生成一份极其详细、专业的投资分析报告。"""
        
        # 构建包含反问问题和用户回答的完整对话
        full_conversation = [
            {'role': 'user', 'content': initial_prompt},
            {'role': 'assistant', 'content': confirmation_questions},
            {'role': 'user', 'content': user_response}
        ]
        
        print(f"📋 用户回答长度: {len(user_response)} 字符")
        
        # 发送包含用户回答的请求
        follow_up_params = {
            'model': 'qwen-deep-research',
            'messages': full_conversation,
            'stream': True,
            'parameters': {
                'max_tokens': 15000,
                'temperature': 0.7
            }
        }
        
        print(f"📤 发送包含用户回答的请求...")
        
        # 调用流式API
        follow_up_responses = Generation.call(**follow_up_params)
        
        final_content = ""
        current_phase = None
        phase_content = ""
        
        print(f"📥 开始接收详细报告...")
        
        for response in follow_up_responses:
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
                    print(f"📝 内容更新: {len(content)} 字符 (累计: {len(final_content)} 字符)")
                
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
                
                # 检查是否完成
                if status == "finished" and phase == "answer":
                    print(f"✅ 最终报告生成完成")
                    break
        
        # 构建完整的报告内容
        complete_report = f"""# 苹果公司 (AAPL) 专业投资分析报告

## 分析确认问题

{confirmation_questions}

## 用户确认回答

{user_response}

## 详细分析报告

{final_content}"""
        
        print(f"\n📊 最终测试结果:")
        print(f"   完整报告长度: {len(complete_report)} 字符")
        print(f"   反问问题长度: {len(confirmation_questions)} 字符")
        print(f"   用户回答长度: {len(user_response)} 字符")
        print(f"   详细报告长度: {len(final_content)} 字符")
        print(f"   内容长度是否符合要求: {'✅ 是' if len(complete_report) >= 3000 else '❌ 否'}")
        
        if complete_report:
            print(f"   完整报告预览: {complete_report[:300]}...")
        
        # 分析内容质量
        if complete_report:
            word_count = len(complete_report.split())
            print(f"   字数统计: {word_count} 字")
            print(f"   平均每字字符数: {len(complete_report)/word_count:.2f}")
            
            # 检查是否包含专业术语
            professional_terms = ['市盈率', '市净率', 'ROE', 'ROA', '毛利率', '净利率', '现金流', '估值', '风险', '投资建议']
            found_terms = [term for term in professional_terms if term in complete_report]
            print(f"   包含专业术语: {found_terms}")
            print(f"   专业术语覆盖率: {len(found_terms)}/{len(professional_terms)} ({len(found_terms)/len(professional_terms)*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试 qwen-deep-research 完整流程...")
    success = test_qwen_deep_research_full()
    
    if success:
        print("\n🎉 测试完成！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)
