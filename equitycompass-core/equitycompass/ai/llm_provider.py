"""
LLM Provider - 多模型AI代理抽象层
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """错误类型枚举"""
    NETWORK_ERROR = "network_error"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION_ERROR = "auth_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    MODEL_ERROR = "model_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    success: bool
    content: str = ""
    error: str = ""
    error_type: ErrorType = ErrorType.UNKNOWN
    tokens_used: int = 0
    response_time: float = 0.0
    retry_count: int = 0
    model_name: str = ""
    provider_name: str = ""


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


class RetryManager:
    """重试管理器"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def should_retry(self, error_type: ErrorType, retry_count: int) -> bool:
        """判断是否应该重试"""
        if retry_count >= self.config.max_retries:
            return False
        
        # 某些错误类型不重试
        no_retry_errors = {ErrorType.AUTHENTICATION_ERROR, ErrorType.QUOTA_EXCEEDED}
        return error_type not in no_retry_errors
    
    def get_delay(self, retry_count: int) -> float:
        """计算重试延迟时间"""
        delay = self.config.base_delay * (self.config.exponential_base ** retry_count)
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def wait(self, retry_count: int):
        """等待重试"""
        delay = self.get_delay(retry_count)
        time.sleep(delay)


class LLMProvider(ABC):
    """LLM Provider 抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'unknown')
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'default')
        self.max_tokens = config.get('max_tokens', 15000)
        self.temperature = config.get('temperature', 0.7)
        
        # 重试配置
        retry_config = config.get('retry_config', {})
        self.retry_config = RetryConfig(
            max_retries=retry_config.get('max_retries', 3),
            base_delay=retry_config.get('base_delay', 1.0),
            max_delay=retry_config.get('max_delay', 60.0),
            exponential_base=retry_config.get('exponential_base', 2.0),
            jitter=retry_config.get('jitter', True)
        )
        self.retry_manager = RetryManager(self.retry_config)
        
        # 超时配置
        self.timeout_config = config.get('timeout_config', {})
        self.request_timeout = self.timeout_config.get('request_timeout', 120)
        self.connect_timeout = self.timeout_config.get('connect_timeout', 30)
    
    @abstractmethod
    def _make_api_request(self, prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """执行API请求（子类实现）"""
        pass
    
    def generate_analysis(self, prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """生成分析报告（带重试机制）"""
        stock_code = stock_info.get('code', 'unknown')
        logger.info(f"开始分析 {stock_code}，使用模型 {self.model}")
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.retry_config.max_retries:
            try:
                start_time = time.time()
                result = self._make_api_request(prompt, stock_info)
                result.response_time = time.time() - start_time
                result.retry_count = retry_count
                result.model_name = self.model
                result.provider_name = self.name
                
                if result.success:
                    logger.info(f"分析成功: {stock_code}, 耗时: {result.response_time:.2f}s")
                    return result
                else:
                    # 分析失败，检查是否需要重试
                    if self.retry_manager.should_retry(result.error_type, retry_count):
                        delay = self.retry_manager.get_delay(retry_count)
                        logger.warning(f"分析失败，{delay:.1f}s后重试: {stock_code}, 错误: {result.error}")
                        self.retry_manager.wait(retry_count)
                        retry_count += 1
                        last_error = result
                        continue
                    else:
                        logger.error(f"分析最终失败: {stock_code}, 错误: {result.error}")
                        return result
                        
            except Exception as e:
                logger.error(f"分析异常: {stock_code}, 错误: {str(e)}")
                error_result = AnalysisResult(
                    success=False,
                    error=str(e),
                    error_type=ErrorType.UNKNOWN,
                    retry_count=retry_count,
                    model_name=self.model,
                    provider_name=self.name
                )
                
                if self.retry_manager.should_retry(ErrorType.UNKNOWN, retry_count):
                    delay = self.retry_manager.get_delay(retry_count)
                    logger.warning(f"异常重试，{delay:.1f}s后重试: {stock_code}")
                    self.retry_manager.wait(retry_count)
                    retry_count += 1
                    last_error = error_result
                    continue
                else:
                    return error_result
        
        # 所有重试都失败了
        if last_error:
            last_error.retry_count = retry_count
            return last_error
        
        return AnalysisResult(
            success=False,
            error="所有重试都失败了",
            error_type=ErrorType.UNKNOWN,
            retry_count=retry_count,
            model_name=self.model,
            provider_name=self.name
        )


class QwenProvider(LLMProvider):
    """通义千问 Provider"""
    
    def _make_api_request(self, prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """实现通义千问API调用"""
        try:
            import requests
            
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "input": {
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
            }
            
            response = requests.post(
                url, 
                json=data, 
                headers=headers,
                timeout=self.request_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("output", {}).get("text", "")
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                
                return AnalysisResult(
                    success=True,
                    content=content,
                    tokens_used=tokens_used
                )
            else:
                error_msg = f"API请求失败: {response.status_code}"
                error_type = self._get_error_type(response.status_code)
                return AnalysisResult(
                    success=False,
                    error=error_msg,
                    error_type=error_type
                )
                
        except requests.exceptions.Timeout:
            return AnalysisResult(
                success=False,
                error="请求超时",
                error_type=ErrorType.TIMEOUT
            )
        except requests.exceptions.RequestException as e:
            return AnalysisResult(
                success=False,
                error=f"网络请求失败: {str(e)}",
                error_type=ErrorType.NETWORK_ERROR
            )
        except Exception as e:
            return AnalysisResult(
                success=False,
                error=f"未知错误: {str(e)}",
                error_type=ErrorType.UNKNOWN
            )
    
    def _get_error_type(self, status_code: int) -> ErrorType:
        """根据状态码确定错误类型"""
        if status_code == 401:
            return ErrorType.AUTHENTICATION_ERROR
        elif status_code == 429:
            return ErrorType.RATE_LIMIT
        elif status_code == 403:
            return ErrorType.QUOTA_EXCEEDED
        else:
            return ErrorType.MODEL_ERROR


class DeepSeekProvider(LLMProvider):
    """DeepSeek Provider"""
    
    def _make_api_request(self, prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """实现DeepSeek API调用"""
        try:
            import requests
            
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=self.request_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                
                return AnalysisResult(
                    success=True,
                    content=content,
                    tokens_used=tokens_used
                )
            else:
                error_msg = f"API请求失败: {response.status_code}"
                error_type = self._get_error_type(response.status_code)
                return AnalysisResult(
                    success=False,
                    error=error_msg,
                    error_type=error_type
                )
                
        except requests.exceptions.Timeout:
            return AnalysisResult(
                success=False,
                error="请求超时",
                error_type=ErrorType.TIMEOUT
            )
        except requests.exceptions.RequestException as e:
            return AnalysisResult(
                success=False,
                error=f"网络请求失败: {str(e)}",
                error_type=ErrorType.NETWORK_ERROR
            )
        except Exception as e:
            return AnalysisResult(
                success=False,
                error=f"未知错误: {str(e)}",
                error_type=ErrorType.UNKNOWN
            )
    
    def _get_error_type(self, status_code: int) -> ErrorType:
        """根据状态码确定错误类型"""
        if status_code == 401:
            return ErrorType.AUTHENTICATION_ERROR
        elif status_code == 429:
            return ErrorType.RATE_LIMIT
        elif status_code == 403:
            return ErrorType.QUOTA_EXCEEDED
        else:
            return ErrorType.MODEL_ERROR


class LLMProviderFactory:
    """LLM Provider 工厂类"""
    
    _providers = {
        'qwen': QwenProvider,
        'deepseek': DeepSeekProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, config: Dict[str, Any]) -> LLMProvider:
        """
        创建 LLM Provider 实例
        
        Args:
            provider_name: 提供商名称
            config: 配置字典
            
        Returns:
            LLM Provider 实例
        """
        if provider_name not in cls._providers:
            raise ValueError(f"不支持的提供商: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(config)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """获取可用的提供商列表"""
        return list(cls._providers.keys())
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """注册新的提供商"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_default_provider(cls) -> LLMProvider:
        """创建默认提供商"""
        default_config = {
            'name': 'qwen',
            'model': 'qwen-turbo',
            'api_key': 'your-api-key',
            'max_tokens': 15000,
            'temperature': 0.7
        }
        return cls.create_provider('qwen', default_config)
