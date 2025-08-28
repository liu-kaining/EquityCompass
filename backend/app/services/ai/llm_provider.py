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
        self.max_tokens = config.get('max_tokens', 8000)
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
            
            # 准备API调用参数 - 使用正确的 DashScope 格式
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
                data["tools"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": "deep_thinking",
                            "description": "启用深度思考模式，让模型进行多步推理",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "thinking_steps": {
                                        "type": "integer",
                                        "description": "思考步数",
                                        "default": self.thinking_steps
                                    }
                                }
                            }
                        }
                    }
                ]
                data["tool_choice"] = {"type": "function", "function": {"name": "deep_thinking"}}
            
            logger.info(f"发送请求到DeepSeek API...")
            # 调用DeepSeek API
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            
            end_time = time.time()
            response_time = end_time - start_time
            logger.info(f"DeepSeek API响应时间: {response_time:.2f}秒, 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"DeepSeek API返回成功 - 股票: {stock_code}")
                
                content = result['choices'][0]['message']['content']
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
