#!/usr/bin/env python3
"""
测试详细分析报告
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

def test_detailed_analysis():
    """测试详细分析报告"""
    
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
        
        print(f"\n🧪 测试详细分析报告")
        
        # 准备请求
        research_prompt = """你是一位顶级的股票分析师，拥有20年以上的投资经验。请对股票 苹果公司 (AAPL) 进行极其深入、详细、专业的投资分析。

要求：
1. 报告必须非常详细，至少3000-5000字
2. 包含大量具体数据、图表分析和专业术语
3. 从多个维度进行全面分析：基本面、技术面、行业分析、风险评估等
4. 提供具体的投资建议和操作策略
5. 使用专业的金融分析框架和方法论
6. 包含定量分析和定性分析
7. 提供风险提示和免责声明

请基于以下信息进行深入分析：
请对苹果公司(AAPL)进行全面的基本面分析，包括公司概况、财务分析、行业分析、风险评估和投资建议。

请生成一份机构级别的专业投资分析报告。"""
        
        api_params = {
            'model': 'qwen-deep-research',
            'messages': [{'role': 'user', 'content': research_prompt}],
            'stream': True,  # qwen-deep-research 目前仅支持流式输出
            'parameters': {
                'max_tokens': 15000,  # 大幅增加token限制，确保生成详细报告
                'temperature': 0.7
            }
        }
        
        print(f"📤 发送详细分析请求")
        print(f"📋 提示词长度: {len(research_prompt)} 字符")
        print(f"🔧 max_tokens: 15000")
        
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
        
        # 如果没有获取到内容，使用阶段内容
        if not final_content and phase_content:
            final_content = phase_content
        
        print(f"\n📊 测试结果:")
        print(f"   最终内容长度: {len(final_content)} 字符")
        print(f"   内容长度是否符合要求: {'✅ 是' if len(final_content) >= 3000 else '❌ 否'}")
        if final_content:
            print(f"   内容预览: {final_content[:300]}...")
        if research_goal:
            print(f"   研究目标: {research_goal}")
        if web_sites:
            print(f"   搜索网站数: {len(web_sites)}")
        
        # 分析内容质量
        if final_content:
            word_count = len(final_content.split())
            print(f"   字数统计: {word_count} 字")
            print(f"   平均每字字符数: {len(final_content)/word_count:.2f}")
            
            # 检查是否包含专业术语
            professional_terms = ['市盈率', '市净率', 'ROE', 'ROA', '毛利率', '净利率', '现金流', '估值', '风险', '投资建议']
            found_terms = [term for term in professional_terms if term in final_content]
            print(f"   包含专业术语: {found_terms}")
            print(f"   专业术语覆盖率: {len(found_terms)}/{len(professional_terms)} ({len(found_terms)/len(professional_terms)*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试详细分析报告...")
    success = test_detailed_analysis()
    
    if success:
        print("\n🎉 测试完成！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)
