"""
LLM Provider抽象层
支持多种大语言模型：Gemini、ChatGPT、Qwen
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import json
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """LLM Provider抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'unknown')
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'default')
        self.max_tokens = config.get('max_tokens', 15000)
        self.temperature = config.get('temperature', 0.7)
    
    @abstractmethod
    def generate_analysis(self, prompt: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成股票分析报告"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试API连接"""
        pass
    
    def format_prompt(self, template: str, stock_info: Dict[str, Any]) -> str:
        """格式化提示词模板"""
        try:
            # 替换模板中的变量
            formatted_prompt = template
            for key, value in stock_info.items():
                placeholder = f"${{{key}}}"
                if placeholder in formatted_prompt:
                    formatted_prompt = formatted_prompt.replace(placeholder, str(value))
            
            return formatted_prompt
        except Exception as e:
            logger.error(f"格式化提示词失败: {str(e)}")
            return template


class GeminiProvider(LLMProvider):
    """Google Gemini Provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.model_name = self.model if self.model else 'gemini-2.0-flash'
    
    def generate_analysis(self, prompt: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """使用Gemini生成分析报告（同步版本）"""
        try:
            import requests
            
            start_time = time.time()
            stock_code = stock_info.get('code', 'unknown')
            
            logger.info(f"开始调用Gemini API - 股票: {stock_code}, 模型: {self.model_name}")
            logger.info(f"Gemini API URL: {self.api_url}")
            logger.info(f"API密钥长度: {len(self.api_key) if self.api_key else 0}")
            
            # 格式化提示词
            formatted_prompt = self.format_prompt(prompt, stock_info)
            logger.info(f"提示词长度: {len(formatted_prompt)} 字符")
            
            # 准备请求数据
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': self.api_key
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": formatted_prompt
                            }
                        ]
                    }
                ]
            }
            
            logger.info(f"发送请求到Gemini API...")
            # 调用Gemini API
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            
            end_time = time.time()
            response_time = end_time - start_time
            logger.info(f"Gemini API响应时间: {response_time:.2f}秒, 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Gemini API返回成功，响应内容长度: {len(str(result))}")
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    usage_metadata = result.get('usageMetadata', {})
                    
                    logger.info(f"Gemini分析成功 - 股票: {stock_code}, 内容长度: {len(content)} 字符")
                    logger.info(f"Token使用情况: {usage_metadata}")
                    
                    return {
                        'success': True,
                        'content': content,
                        'provider': 'gemini',
                        'model': self.model_name,
                        'tokens_used': usage_metadata.get('totalTokenCount'),
                        'response_time': response_time,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    logger.error(f"Gemini API返回成功但无内容 - 股票: {stock_code}, 响应: {result}")
                    return {
                        'success': False,
                        'error': 'No response content',
                        'provider': 'gemini',
                        'timestamp': datetime.utcnow().isoformat()
                    }
            else:
                logger.error(f"Gemini API请求失败 - 股票: {stock_code}, 状态码: {response.status_code}, 响应: {response.text}")
                return {
                    'success': False,
                    'error': f'API request failed: {response.status_code} - {response.text}',
                    'provider': 'gemini',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Gemini生成分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'gemini',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def test_connection(self) -> bool:
        """测试Gemini连接"""
        try:
            import requests
            
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': self.api_key
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Hello"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return 'candidates' in result and len(result['candidates']) > 0
            else:
                logger.error(f"Gemini连接测试失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Gemini连接测试失败: {str(e)}")
            return False



class QwenProvider(LLMProvider):
    """阿里云通义千问 Provider - 支持深度思考和全网搜索"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 深度思考和全网搜索相关配置
        self.enable_deep_thinking = config.get('enable_deep_thinking', True)
        self.enable_web_search = config.get('enable_web_search', True)
        self.thinking_steps = config.get('thinking_steps', 3)  # 思考步数
        
        try:
            import dashscope
            dashscope.api_key = self.api_key
        except ImportError:
            logger.error("DashScope库未安装，请运行: pip install dashscope")
            raise
        except Exception as e:
            logger.error(f"初始化Qwen失败: {str(e)}")
            raise
    
    def generate_analysis(self, prompt: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """使用Qwen生成分析报告（同步版本）"""
        try:
            start_time = time.time()
            stock_code = stock_info.get('code', 'unknown')
            
            logger.info(f"开始调用Qwen API - 股票: {stock_code}, 模型: {self.model}")
            logger.info(f"Qwen API密钥长度: {len(self.api_key) if self.api_key else 0}")
            
            # 格式化提示词
            formatted_prompt = self.format_prompt(prompt, stock_info)
            logger.info(f"Qwen提示词长度: {len(formatted_prompt)} 字符")
            
            # 调用Qwen API
            from dashscope import Generation
            logger.info(f"发送请求到Qwen API...")
            
            # 检查是否是 qwen-deep-research 模型
            if self.model == 'qwen-deep-research':
                # qwen-deep-research 模型需要特殊的调用方式
                logger.info("使用 qwen-deep-research 模型进行深入研究分析")
                
                # 构建研究提示词
                research_prompt = f"""请对股票 {stock_info.get('name', '')} ({stock_info.get('code', '')}) 进行极其深入、详细、专业的投资分析。

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
{formatted_prompt}

请在反问确认阶段就提供详细的分析框架和关键问题，然后在研究阶段生成极其详细、专业的投资分析报告。"""
                
                api_params = {
                    'model': self.model,
                    'messages': [{'role': 'user', 'content': research_prompt}],
                    'stream': True,  # qwen-deep-research 目前仅支持流式输出
                    'parameters': {
                        'max_tokens': 15000,  # 大幅增加token限制，确保生成详细报告
                        'temperature': 0.7
                    }
                }
                
                # 处理流式响应 - 支持反问确认流程
                return self._process_deep_research_response_with_confirmation(api_params, stock_code, response_time=0)
            else:
                # 其他模型使用原有方式
                api_params = {
                    'model': self.model,
                    'prompt': formatted_prompt,  # 使用 prompt 参数
                    'parameters': {
                        'max_tokens': self.max_tokens,
                        'temperature': self.temperature,
                        'result_format': 'message'
                    }
                }
                
                # 如果启用深度思考或全网搜索，添加工具参数
                if self.enable_deep_thinking or self.enable_web_search:
                    api_params['parameters']['tools'] = []
                    
                    # 如果启用深度思考，添加相关参数
                    if self.enable_deep_thinking:
                        api_params['parameters']['tools'].append({
                            'type': 'function',
                            'function': {
                                'name': 'deep_thinking',
                                'description': '启用深度思考模式，让模型进行多步推理',
                                'parameters': {
                                    'type': 'object',
                                    'properties': {
                                        'thinking_steps': {
                                            'type': 'integer',
                                            'description': '思考步数',
                                            'default': self.thinking_steps
                                        }
                                    }
                                }
                            }
                        })
                    
                    # 如果启用全网搜索，添加搜索参数
                    if self.enable_web_search:
                        api_params['parameters']['tools'].append({
                            'type': 'function',
                            'function': {
                                'name': 'web_search',
                                'description': '启用全网搜索功能，获取最新信息',
                                'parameters': {
                                    'type': 'object',
                                    'properties': {
                                        'query': {
                                            'type': 'string',
                                            'description': '搜索查询',
                                            'default': f"{stock_info.get('name', '')} {stock_info.get('code', '')} 股票分析 最新消息"
                                        }
                                    }
                                }
                            }
                        })
                
                response = Generation.call(**api_params)
            
            end_time = time.time()
            response_time = end_time - start_time
            logger.info(f"Qwen API响应时间: {response_time:.2f}秒, 状态码: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"Qwen API返回成功 - 股票: {stock_code}")
                
                # 从response中提取文本内容
                try:
                    if hasattr(response, 'output') and response.output:
                        if hasattr(response.output, 'choices') and response.output.choices:
                            content = response.output.choices[0].message.content
                        elif hasattr(response.output, 'text') and response.output.text:
                            content = response.output.text
                        else:
                            content = str(response.output)
                    else:
                        # 尝试直接访问 response 的属性
                        content = str(response)
                    
                    logger.info(f"Qwen分析成功 - 股票: {stock_code}, 内容长度: {len(content)} 字符")
                except Exception as e:
                    logger.error(f"解析Qwen响应失败: {str(e)}")
                    content = f"Qwen分析完成，但解析响应时出现问题: {str(e)}"
                
                return {
                    'success': True,
                    'content': content,
                    'provider': 'qwen',
                    'model': self.model,
                    'tokens_used': getattr(response.usage, 'total_tokens', None) if hasattr(response, 'usage') else None,
                    'response_time': response_time,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                error_msg = getattr(response, 'message', f"HTTP {response.status_code}")
                logger.error(f"Qwen API请求失败 - 股票: {stock_code}, 错误: {error_msg}")
                raise Exception(f"Qwen API错误: {error_msg}")
            
        except Exception as e:
            logger.error(f"Qwen生成分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'qwen',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def test_connection(self) -> bool:
        """测试Qwen连接"""
        try:
            from dashscope import Generation
            
            # 基础测试参数 - 使用正确的 DashScope 格式
            api_params = {
                'model': self.model,
                'prompt': "Hello",  # 使用 prompt 参数
                'parameters': {
                    'max_tokens': 10,
                    'result_format': 'message'
                }
            }
            
            # 如果启用深度思考，添加测试参数
            if self.enable_deep_thinking:
                api_params['parameters']['tools'] = [
                    {
                        'type': 'function',
                        'function': {
                            'name': 'deep_thinking',
                            'description': '启用深度思考模式',
                            'parameters': {
                                'type': 'object',
                                'properties': {
                                    'thinking_steps': {
                                        'type': 'integer',
                                        'description': '思考步数',
                                        'default': 1
                                    }
                                }
                            }
                        }
                    }
                ]
            
            response = Generation.call(**api_params)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Qwen连接测试失败: {str(e)}")
            return False
    
    def _process_deep_research_response(self, api_params: Dict[str, Any], stock_code: str, response_time: float) -> Dict[str, Any]:
        """处理 qwen-deep-research 模型的流式响应"""
        try:
            from dashscope import Generation
            
            logger.info(f"开始处理 qwen-deep-research 流式响应 - 股票: {stock_code}")
            
            # 调用流式API
            responses = Generation.call(**api_params)
            
            current_phase = None
            phase_content = ""
            final_content = ""
            research_goal = ""
            web_sites = []
            
            for response in responses:
                # 检查响应状态码
                if hasattr(response, 'status_code') and response.status_code != 200:
                    logger.error(f"qwen-deep-research HTTP返回码：{response.status_code}")
                    if hasattr(response, 'code'):
                        logger.error(f"错误码：{response.code}")
                    if hasattr(response, 'message'):
                        logger.error(f"错误信息：{response.message}")
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
                            logger.info(f"qwen-deep-research {current_phase} 阶段完成")
                        current_phase = phase
                        phase_content = ""
                        logger.info(f"qwen-deep-research 进入 {phase} 阶段")
                    
                    # 累积阶段内容
                    if content:
                        phase_content += content
                        final_content += content
                    
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
                                        logger.info(f"qwen-deep-research 研究目标: {goal}")
                            
                            # 处理streamingWebResult状态
                            elif status == "streamingWebResult":
                                if 'webSites' in research_info:
                                    sites = research_info['webSites']
                                    if sites and len(sites) > len(web_sites):
                                        web_sites = sites
                                        logger.info(f"qwen-deep-research 发现 {len(sites)} 个网站")
                    
                    # 检查是否完成
                    if status == "finished" and phase == "answer":
                        logger.info(f"qwen-deep-research 最终报告生成完成")
                        break
            
            # 如果没有获取到内容，使用阶段内容
            if not final_content and phase_content:
                final_content = phase_content
            
            logger.info(f"qwen-deep-research 分析成功 - 股票: {stock_code}, 内容长度: {len(final_content)} 字符")
            
            return {
                'success': True,
                'content': final_content,
                'provider': 'qwen',
                'model': self.model,
                'tokens_used': None,  # 流式响应可能没有token信息
                'response_time': response_time,
                'timestamp': datetime.utcnow().isoformat(),
                'research_goal': research_goal,
                'web_sites': web_sites
            }
            
        except Exception as e:
            logger.error(f"qwen-deep-research 处理失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'qwen',
                'model': self.model,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _process_deep_research_response_with_confirmation(self, api_params: Dict[str, Any], stock_code: str, response_time: float) -> Dict[str, Any]:
        """处理 qwen-deep-research 模型的流式响应，支持反问确认流程"""
        try:
            from dashscope import Generation
            
            logger.info(f"开始处理 qwen-deep-research 流式响应（支持反问确认）- 股票: {stock_code}")
            
            # 第一步：获取反问确认问题
            logger.info("第一步：获取反问确认问题")
            responses = Generation.call(**api_params)
            
            current_phase = None
            phase_content = ""
            confirmation_questions = ""
            
            for response in responses:
                if hasattr(response, 'status_code') and response.status_code != 200:
                    logger.error(f"qwen-deep-research HTTP返回码：{response.status_code}")
                    continue
                
                if hasattr(response, 'output') and response.output:
                    message = response.output.get('message', {})
                    phase = message.get('phase')
                    content = message.get('content', '')
                    status = message.get('status')
                    
                    if phase != current_phase:
                        if current_phase and phase_content:
                            logger.info(f"qwen-deep-research {current_phase} 阶段完成")
                        current_phase = phase
                        phase_content = ""
                        logger.info(f"qwen-deep-research 进入 {phase} 阶段")
                    
                    if content:
                        phase_content += content
                        
                        # 如果是反问确认阶段，记录问题
                        if phase == "answer" and status == "typing":
                            confirmation_questions += content
                    
                    # 检查反问确认是否完成
                    if status == "finished" and phase == "answer":
                        logger.info("反问确认阶段完成")
                        break
            
            # 第二步：自动回答反问问题并继续分析
            if confirmation_questions:
                logger.info("第二步：自动回答反问问题并继续分析")
                
                # 构建自动回答
                auto_response = """基于您的分析需求，我提供以下确认信息：

1. 投资时间框架：我希望分析涵盖短期（6个月）、中期（1-2年）和长期（3-5年）三个时间维度，重点关注中长期投资价值，但也要包含短期交易机会的识别。

2. 财务分析重点：请重点分析自由现金流折现（DCF）、ROIC趋势、毛利率和净利率变化、资本回报率等关键指标，同时包含相对估值法（P/E、P/S、EV/EBITDA）的对比分析。

3. 行业分析范围：请深入分析公司与主要竞争对手在生态系统、技术创新、市场份额等方面的对比，特别关注公司在高端市场的护城河效应。

4. 技术面分析：请结合短期技术指标（支撑阻力、动量指标）和长期趋势结构（周线级别波浪理论、机构持仓变化）进行多维度分析。

5. 风险因素：请重点关注供应链风险、监管风险、技术颠覆风险、地缘政治风险等关键不确定性因素。

请基于以上确认信息，生成一份极其详细、专业的投资分析报告。"""
                
                # 构建包含反问问题和自动回答的完整对话
                full_conversation = [
                    {'role': 'user', 'content': api_params['messages'][0]['content']},
                    {'role': 'assistant', 'content': confirmation_questions},
                    {'role': 'user', 'content': auto_response}
                ]
                
                # 发送包含自动回答的请求
                follow_up_params = {
                    'model': self.model,
                    'messages': full_conversation,
                    'stream': True,
                    'parameters': {
                        'max_tokens': 15000,
                        'temperature': 0.7
                    }
                }
                
                logger.info("发送包含自动回答的请求...")
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
                        
                        # 处理WebResearch阶段的特殊信息
                        if phase == "WebResearch":
                            if extra.get('deep_research', {}).get('research'):
                                research_info = extra['deep_research']['research']
                                
                                if status == "streamingQueries":
                                    if 'researchGoal' in research_info:
                                        goal = research_info['researchGoal']
                                        if goal and goal != research_goal:
                                            research_goal = goal
                                            logger.info(f"qwen-deep-research 研究目标: {goal}")
                                
                                elif status == "streamingWebResult":
                                    if 'webSites' in research_info:
                                        sites = research_info['webSites']
                                        if sites and len(sites) > len(web_sites):
                                            web_sites = sites
                                            logger.info(f"qwen-deep-research 发现 {len(sites)} 个网站")
                        
                        if status == "finished" and phase == "answer":
                            logger.info("最终报告生成完成")
                            break
            
            # 构建完整的报告内容
            complete_report = ""
            
            # 如果有反问确认问题，添加到报告中
            if confirmation_questions:
                complete_report += f"## 分析确认问题\n\n{confirmation_questions}\n\n"
                complete_report += "## 详细分析报告\n\n"
            
            # 添加最终分析内容
            complete_report += final_content
            
            logger.info(f"qwen-deep-research 分析成功 - 股票: {stock_code}, 内容长度: {len(complete_report)} 字符")
            
            return {
                'success': True,
                'content': complete_report,
                'provider': 'qwen',
                'model': self.model,
                'tokens_used': None,
                'response_time': response_time,
                'timestamp': datetime.utcnow().isoformat(),
                'research_goal': research_goal,
                'web_sites': web_sites,
                'confirmation_questions': confirmation_questions
            }
            
        except Exception as e:
            logger.error(f"qwen-deep-research 处理失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'qwen',
                'model': self.model,
                'timestamp': datetime.utcnow().isoformat()
            }


class DeepSeekProvider(LLMProvider):
    """DeepSeek Provider - 支持深度思考模型"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        # 深度思考相关配置
        self.enable_deep_thinking = config.get('enable_deep_thinking', True)
        self.thinking_steps = config.get('thinking_steps', 3)  # 思考步数
    
    def generate_analysis(self, prompt: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """使用DeepSeek生成分析报告（同步版本）"""
        try:
            import requests
            
            start_time = time.time()
            stock_code = stock_info.get('code', 'unknown')
            
            logger.info(f"开始调用DeepSeek API - 股票: {stock_code}, 模型: {self.model}")
            logger.info(f"DeepSeek API URL: {self.api_url}")
            logger.info(f"DeepSeek API密钥长度: {len(self.api_key) if self.api_key else 0}")
            
            # 格式化提示词
            formatted_prompt = self.format_prompt(prompt, stock_info)
            logger.info(f"DeepSeek提示词长度: {len(formatted_prompt)} 字符")
            
            # 准备请求数据
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # 基础请求数据
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的股票分析师，请根据提供的信息进行专业的股票分析。请深入思考，提供详细的分析和投资建议。"},
                    {"role": "user", "content": formatted_prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # 如果启用深度思考，添加相关参数
            if self.enable_deep_thinking:
                # deepseek-reasoner 不支持 Function Calling，直接使用其推理能力
                # 在系统消息中强调深度思考
                data["messages"][0]["content"] = "你是一个专业的股票分析师，请根据提供的信息进行专业的股票分析。请深入思考，进行多步推理，提供详细的分析和投资建议。"
                logger.info("DeepSeek Reasoner 使用内置推理能力，无需工具调用")
            
            logger.info(f"发送请求到DeepSeek API...")
            # 调用DeepSeek API
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            
            end_time = time.time()
            response_time = end_time - start_time
            logger.info(f"DeepSeek API响应时间: {response_time:.2f}秒, 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"DeepSeek API返回成功 - 股票: {stock_code}")
                
                message = result['choices'][0]['message']
                content = ""
                
                # 处理不同的响应格式
                if 'content' in message and message['content']:
                    # 基础响应格式
                    content = message['content']
                elif 'reasoning_content' in message and message['reasoning_content']:
                    # 推理内容格式
                    content = message['reasoning_content']
                elif 'tool_calls' in message and message['tool_calls']:
                    # 工具调用格式 - 需要处理 tool_calls
                    logger.info(f"检测到工具调用，需要进一步处理")
                    # 对于工具调用，我们需要发送后续请求来获取最终结果
                    # 暂时返回一个提示信息
                    content = "深度思考模式已启用，正在处理推理结果..."
                else:
                    logger.warning(f"DeepSeek响应格式未知: {message}")
                    content = "响应格式异常，请检查API配置"
                
                logger.info(f"DeepSeek分析成功 - 股票: {stock_code}, 内容长度: {len(content)} 字符")
                
                return {
                    'success': True,
                    'content': content,
                    'provider': 'deepseek',
                    'model': self.model,
                    'tokens_used': result['usage']['total_tokens'] if 'usage' in result else None,
                    'response_time': response_time,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"DeepSeek API请求失败 - 股票: {stock_code}, 状态码: {response.status_code}, 响应: {response.text}")
                return {
                    'success': False,
                    'error': f'API request failed: {response.status_code} - {response.text}',
                    'provider': 'deepseek',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error(f"DeepSeek生成分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'deepseek',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def test_connection(self) -> bool:
        """测试DeepSeek连接"""
        try:
            import requests
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # 基础测试数据
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            # 如果启用深度思考，添加测试参数
            if self.enable_deep_thinking:
                data["tools"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": "deep_thinking",
                            "description": "启用深度思考模式",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "thinking_steps": {
                                        "type": "integer",
                                        "description": "思考步数",
                                        "default": 1
                                    }
                                }
                            }
                        }
                    }
                ]
                data["tool_choice"] = {"type": "function", "function": {"name": "deep_thinking"}}
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'] is not None
            else:
                logger.error(f"DeepSeek连接测试失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"DeepSeek连接测试失败: {str(e)}")
            return False


class LLMProviderFactory:
    """LLM Provider工厂类"""
    
    @staticmethod
    def create_provider(provider_name: str, config: Dict[str, Any]) -> LLMProvider:
        """创建LLM Provider实例"""
        provider_name = provider_name.lower()
        
        if provider_name == 'gemini':
            return GeminiProvider(config)
        elif provider_name == 'qwen':
            return QwenProvider(config)
        elif provider_name == 'deepseek':
            return DeepSeekProvider(config)
        else:
            raise ValueError(f"不支持的Provider类型: {provider_name}")
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """获取可用的Provider列表"""
        return ['qwen', 'deepseek']
    
    @staticmethod
    def test_provider(provider_type: str, config: Dict[str, Any]) -> bool:
        """测试Provider连接"""
        try:
            provider = LLMProviderFactory.create_provider(provider_type, config)
            return provider.test_connection()
        except Exception as e:
            logger.error(f"测试Provider失败: {str(e)}")
            return False
