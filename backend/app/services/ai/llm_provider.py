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
        self.max_tokens = config.get('max_tokens', 2000)
        self.temperature = config.get('temperature', 0.7)
    
    @abstractmethod
    async def generate_analysis(self, prompt: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成股票分析报告"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
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
            
            # 格式化提示词
            formatted_prompt = self.format_prompt(prompt, stock_info)
            
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
            
            # 调用Gemini API
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    usage_metadata = result.get('usageMetadata', {})
                    
                    return {
                        'success': True,
                        'content': content,
                        'provider': 'gemini',
                        'model': self.model_name,
                        'tokens_used': usage_metadata.get('totalTokenCount'),
                        'response_time': end_time - start_time,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No response content',
                        'provider': 'gemini',
                        'timestamp': datetime.utcnow().isoformat()
                    }
            else:
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


class ChatGPTProvider(LLMProvider):
    """OpenAI ChatGPT Provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            logger.error("OpenAI库未安装")
            raise
        except Exception as e:
            logger.error(f"初始化ChatGPT失败: {str(e)}")
            raise
    
    def generate_analysis(self, prompt: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """使用ChatGPT生成分析报告（同步版本）"""
        try:
            start_time = time.time()
            
            # 格式化提示词
            formatted_prompt = self.format_prompt(prompt, stock_info)
            
            # 调用ChatGPT API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的股票分析师，请根据提供的信息进行专业的股票分析。"},
                    {"role": "user", "content": formatted_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            end_time = time.time()
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'provider': 'chatgpt',
                'model': self.model,
                'tokens_used': response.usage.total_tokens,
                'response_time': end_time - start_time,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ChatGPT生成分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'chatgpt',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def test_connection(self) -> bool:
        """测试ChatGPT连接"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return response.choices[0].message.content is not None
        except Exception as e:
            logger.error(f"ChatGPT连接测试失败: {str(e)}")
            return False


class QwenProvider(LLMProvider):
    """阿里云通义千问 Provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import dashscope
            dashscope.api_key = self.api_key
        except ImportError:
            logger.error("DashScope库未安装")
            raise
        except Exception as e:
            logger.error(f"初始化Qwen失败: {str(e)}")
            raise
    
    def generate_analysis(self, prompt: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """使用Qwen生成分析报告（同步版本）"""
        try:
            start_time = time.time()
            
            # 格式化提示词
            formatted_prompt = self.format_prompt(prompt, stock_info)
            
            # 调用Qwen API
            from dashscope import Generation
            response = Generation.call(
                model=self.model,
                prompt=formatted_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'content': response.output.text,
                    'provider': 'qwen',
                    'model': self.model,
                    'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else None,
                    'response_time': end_time - start_time,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                raise Exception(f"Qwen API错误: {response.message}")
            
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
            response = Generation.call(
                model=self.model,
                prompt="Hello",
                max_tokens=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Qwen连接测试失败: {str(e)}")
            return False


class DeepSeekProvider(LLMProvider):
    """DeepSeek Provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
    
    def generate_analysis(self, prompt: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """使用DeepSeek生成分析报告（同步版本）"""
        try:
            import requests
            
            start_time = time.time()
            
            # 格式化提示词
            formatted_prompt = self.format_prompt(prompt, stock_info)
            
            # 准备请求数据
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的股票分析师，请根据提供的信息进行专业的股票分析。"},
                    {"role": "user", "content": formatted_prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # 调用DeepSeek API
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'content': result['choices'][0]['message']['content'],
                    'provider': 'deepseek',
                    'model': self.model,
                    'tokens_used': result['usage']['total_tokens'] if 'usage' in result else None,
                    'response_time': end_time - start_time,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
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
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
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
    
    _providers = {
        'gemini': GeminiProvider,
        'chatgpt': ChatGPTProvider,
        'qwen': QwenProvider,
        'deepseek': DeepSeekProvider
    }
    
    @classmethod
    def create_provider(cls, provider_type: str, config: Dict[str, Any]) -> LLMProvider:
        """创建LLM Provider实例"""
        if provider_type not in cls._providers:
            raise ValueError(f"不支持的Provider类型: {provider_type}")
        
        provider_class = cls._providers[provider_type]
        return provider_class(config)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """获取可用的Provider列表"""
        return list(cls._providers.keys())
    
    @classmethod
    def test_provider(cls, provider_type: str, config: Dict[str, Any]) -> bool:
        """测试Provider连接"""
        try:
            provider = cls.create_provider(provider_type, config)
            return provider.test_connection()
        except Exception as e:
            logger.error(f"测试Provider失败: {str(e)}")
            return False
