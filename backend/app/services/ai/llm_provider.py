"""
LLM Provider抽象层
支持多种大语言模型：Gemini、ChatGPT、Qwen
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import logging
import json
import time
import random
import requests
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """错误类型枚举"""
    NETWORK_ERROR = "network_error"
    API_ERROR = "api_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    TIMEOUT_ERROR = "timeout_error"
    PARSE_ERROR = "parse_error"
    UNKNOWN_ERROR = "unknown_error"


class StructuredLogger:
    """结构化日志记录器"""
    
    @staticmethod
    def log_api_call(provider: str, model: str, stock_code: str, action: str, **kwargs):
        """记录API调用日志"""
        log_data = {
            'provider': provider,
            'model': model,
            'stock_code': stock_code,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.info(f"API调用 - {provider}:{model} - {stock_code} - {action}", extra=log_data)
    
    @staticmethod
    def log_api_success(provider: str, model: str, stock_code: str, response_time: float, tokens_used: int = None, **kwargs):
        """记录API成功日志"""
        log_data = {
            'provider': provider,
            'model': model,
            'stock_code': stock_code,
            'response_time': response_time,
            'tokens_used': tokens_used,
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.info(f"API成功 - {provider}:{model} - {stock_code} - {response_time:.2f}s", extra=log_data)
    
    @staticmethod
    def log_api_error(provider: str, model: str, stock_code: str, error_type: ErrorType, error_msg: str, retry_count: int = 0, **kwargs):
        """记录API错误日志"""
        log_data = {
            'provider': provider,
            'model': model,
            'stock_code': stock_code,
            'error_type': error_type.value,
            'error_msg': error_msg,
            'retry_count': retry_count,
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.error(f"API错误 - {provider}:{model} - {stock_code} - {error_type.value} - {error_msg}", extra=log_data)
    
    @staticmethod
    def log_retry_attempt(provider: str, model: str, stock_code: str, retry_count: int, delay: float, error_type: ErrorType):
        """记录重试尝试日志"""
        log_data = {
            'provider': provider,
            'model': model,
            'stock_code': stock_code,
            'retry_count': retry_count,
            'delay': delay,
            'error_type': error_type.value,
            'action': 'retry',
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.warning(f"重试尝试 - {provider}:{model} - {stock_code} - 第{retry_count}次 - 延迟{delay:.2f}s", extra=log_data)


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_errors: List[ErrorType] = None
    
    def __post_init__(self):
        if self.retryable_errors is None:
            self.retryable_errors = [
                ErrorType.NETWORK_ERROR,
                ErrorType.RATE_LIMIT_ERROR,
                ErrorType.TIMEOUT_ERROR,
                ErrorType.API_ERROR
            ]


@dataclass
class AnalysisResult:
    """标准化的分析结果"""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    timestamp: Optional[str] = None
    retry_count: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}


class RetryManager:
    """重试管理器"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def should_retry(self, error_type: ErrorType, retry_count: int) -> bool:
        """判断是否应该重试"""
        if retry_count >= self.config.max_retries:
            return False
        return error_type in self.config.retryable_errors
    
    def get_delay(self, retry_count: int) -> float:
        """计算重试延迟时间"""
        delay = self.config.base_delay * (self.config.exponential_base ** retry_count)
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            # 添加随机抖动，避免雷群效应
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def wait(self, retry_count: int):
        """等待重试"""
        delay = self.get_delay(retry_count)
        logger.info(f"等待 {delay:.2f} 秒后重试 (第 {retry_count + 1} 次)")
        time.sleep(delay)


class LLMProvider(ABC):
    """LLM Provider抽象基类"""
    
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
        self.request_timeout = self.timeout_config.get('request_timeout', 120)  # 增加到120秒
        self.connect_timeout = self.timeout_config.get('connect_timeout', 30)
    
    @abstractmethod
    def _make_api_request(self, prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """执行API请求（子类实现）"""
        pass
    
    def generate_analysis(self, prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """生成股票分析报告（带重试机制）"""
        stock_code = stock_info.get('code', 'unknown')
        StructuredLogger.log_api_call(self.name, self.model, stock_code, 'start_analysis')
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.retry_config.max_retries:
            try:
                start_time = time.time()
                result = self._make_api_request(prompt, stock_info)
                result.response_time = time.time() - start_time
                result.retry_count = retry_count
                
                if result.success:
                    StructuredLogger.log_api_success(
                        self.name, self.model, stock_code, 
                        result.response_time, result.tokens_used,
                        retry_count=retry_count
                    )
                    return result
                else:
                    # 分析失败，检查是否需要重试
                    if self.retry_manager.should_retry(result.error_type, retry_count):
                        delay = self.retry_manager.get_delay(retry_count)
                        StructuredLogger.log_retry_attempt(
                            self.name, self.model, stock_code, 
                            retry_count + 1, delay, result.error_type
                        )
                        self.retry_manager.wait(retry_count)
                        retry_count += 1
                        last_error = result
                        continue
                    else:
                        StructuredLogger.log_api_error(
                            self.name, self.model, stock_code,
                            result.error_type, result.error, retry_count
                        )
                        return result
                        
            except Exception as e:
                error_type = self._classify_error(e)
                error_result = AnalysisResult(
                    success=False,
                    error=str(e),
                    error_type=error_type,
                    provider=self.name,
                    model=self.model,
                    retry_count=retry_count
                )
                
                if self.retry_manager.should_retry(error_type, retry_count):
                    delay = self.retry_manager.get_delay(retry_count)
                    StructuredLogger.log_retry_attempt(
                        self.name, self.model, stock_code,
                        retry_count + 1, delay, error_type
                    )
                    self.retry_manager.wait(retry_count)
                    retry_count += 1
                    last_error = error_result
                    continue
                else:
                    StructuredLogger.log_api_error(
                        self.name, self.model, stock_code,
                        error_type, str(e), retry_count
                    )
                    return error_result
        
        # 所有重试都失败了
        if last_error:
            last_error.retry_count = retry_count
            StructuredLogger.log_api_error(
                self.name, self.model, stock_code,
                last_error.error_type, f"所有重试都失败，总重试次数: {retry_count}", retry_count
            )
            return last_error
        else:
            return AnalysisResult(
                success=False,
                error="未知错误",
                error_type=ErrorType.UNKNOWN_ERROR,
                provider=self.name,
                model=self.model,
                retry_count=retry_count
            )
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """分类错误类型"""
        error_str = str(error).lower()
        
        if isinstance(error, requests.exceptions.Timeout):
            return ErrorType.TIMEOUT_ERROR
        elif isinstance(error, requests.exceptions.ConnectionError):
            return ErrorType.NETWORK_ERROR
        elif isinstance(error, requests.exceptions.HTTPError):
            if "401" in error_str or "403" in error_str:
                return ErrorType.AUTHENTICATION_ERROR
            elif "429" in error_str:
                return ErrorType.RATE_LIMIT_ERROR
            else:
                return ErrorType.API_ERROR
        elif "timeout" in error_str:
            return ErrorType.TIMEOUT_ERROR
        elif "connection" in error_str or "network" in error_str:
            return ErrorType.NETWORK_ERROR
        elif "authentication" in error_str or "unauthorized" in error_str:
            return ErrorType.AUTHENTICATION_ERROR
        elif "rate limit" in error_str or "quota" in error_str:
            return ErrorType.RATE_LIMIT_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
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
    
    def _make_api_request(self, prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """执行Gemini API请求"""
        stock_code = stock_info.get('code', 'unknown')
        
        logger.info(f"调用Gemini API - 股票: {stock_code}, 模型: {self.model_name}")
        logger.debug(f"API URL: {self.api_url}")
        logger.debug(f"API密钥长度: {len(self.api_key) if self.api_key else 0}")
        
        # 格式化提示词
        formatted_prompt = self.format_prompt(prompt, stock_info)
        logger.debug(f"提示词长度: {len(formatted_prompt)} 字符")
        
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
        
        try:
            # 调用Gemini API，使用新的超时配置
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                timeout=(self.connect_timeout, self.request_timeout)
            )
            
            logger.debug(f"Gemini API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"Gemini API返回成功，响应内容长度: {len(str(result))}")
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    usage_metadata = result.get('usageMetadata', {})
                    
                    logger.info(f"Gemini分析成功 - 股票: {stock_code}, 内容长度: {len(content)} 字符")
                    logger.debug(f"Token使用情况: {usage_metadata}")
                    
                    return AnalysisResult(
                        success=True,
                        content=content,
                        provider='gemini',
                        model=self.model_name,
                        tokens_used=usage_metadata.get('totalTokenCount'),
                        metadata={'usage_metadata': usage_metadata}
                    )
                else:
                    logger.error(f"Gemini API返回成功但无内容 - 股票: {stock_code}")
                    return AnalysisResult(
                        success=False,
                        error='No response content from Gemini API',
                        error_type=ErrorType.PARSE_ERROR,
                        provider='gemini',
                        model=self.model_name
                    )
            else:
                # 根据状态码分类错误
                error_type = self._classify_http_error(response.status_code)
                error_msg = f'Gemini API request failed: {response.status_code} - {response.text}'
                
                logger.error(f"Gemini API请求失败 - 股票: {stock_code}, 状态码: {response.status_code}")
                
                return AnalysisResult(
                    success=False,
                    error=error_msg,
                    error_type=error_type,
                    provider='gemini',
                    model=self.model_name
                )
                
        except requests.exceptions.Timeout:
            logger.error(f"Gemini API请求超时 - 股票: {stock_code}")
            return AnalysisResult(
                success=False,
                error='Request timeout',
                error_type=ErrorType.TIMEOUT_ERROR,
                provider='gemini',
                model=self.model_name
            )
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Gemini API连接错误 - 股票: {stock_code}, 错误: {str(e)}")
            return AnalysisResult(
                success=False,
                error=f'Connection error: {str(e)}',
                error_type=ErrorType.NETWORK_ERROR,
                provider='gemini',
                model=self.model_name
            )
        except Exception as e:
            logger.error(f"Gemini API请求异常 - 股票: {stock_code}, 错误: {str(e)}")
            return AnalysisResult(
                success=False,
                error=str(e),
                error_type=ErrorType.UNKNOWN_ERROR,
                provider='gemini',
                model=self.model_name
            )
    
    def _classify_http_error(self, status_code: int) -> ErrorType:
        """根据HTTP状态码分类错误类型"""
        if status_code == 401 or status_code == 403:
            return ErrorType.AUTHENTICATION_ERROR
        elif status_code == 429:
            return ErrorType.RATE_LIMIT_ERROR
        elif 400 <= status_code < 500:
            return ErrorType.API_ERROR
        elif 500 <= status_code < 600:
            return ErrorType.NETWORK_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def test_connection(self) -> bool:
        """测试Gemini连接"""
        try:
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
            
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                timeout=(self.connect_timeout, 30)  # 测试连接使用较短的超时时间
            )
            
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
    
    def _make_api_request(self, prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """执行Qwen API请求"""
        stock_code = stock_info.get('code', 'unknown')
        
        logger.info(f"调用Qwen API - 股票: {stock_code}, 模型: {self.model}")
        logger.debug(f"API密钥长度: {len(self.api_key) if self.api_key else 0}")
        
        # 格式化提示词
        formatted_prompt = self.format_prompt(prompt, stock_info)
        logger.debug(f"提示词长度: {len(formatted_prompt)} 字符")
        
        try:
            from dashscope import Generation
            
            # 检查是否是特殊模型
            if self.model == 'qwen-deep-research':
                logger.info("使用 qwen-deep-research 模型进行深入研究分析")
                return self._handle_deep_research_model(formatted_prompt, stock_info)
            elif self.model == 'qwen-max-preview':
                logger.info("使用 qwen-max-preview 模型进行高级分析")
                return self._handle_max_preview_model(formatted_prompt, stock_info)
            else:
                # 其他模型使用标准方式
                return self._handle_standard_model(formatted_prompt, stock_info)
                
        except ImportError:
            logger.error("DashScope库未安装")
            return AnalysisResult(
                success=False,
                error="DashScope库未安装，请运行: pip install dashscope",
                error_type=ErrorType.UNKNOWN_ERROR,
                provider='qwen',
                model=self.model
            )
        except Exception as e:
            logger.error(f"Qwen API请求异常 - 股票: {stock_code}, 错误: {str(e)}")
            return AnalysisResult(
                success=False,
                error=str(e),
                error_type=ErrorType.UNKNOWN_ERROR,
                provider='qwen',
                model=self.model
            )
    
    def _handle_standard_model(self, formatted_prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """处理标准模型请求"""
        from dashscope import Generation
        
        stock_code = stock_info.get('code', 'unknown')
        
        api_params = {
            'model': self.model,
            'prompt': formatted_prompt,
            'parameters': {
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'result_format': 'message'
            }
        }
        
        # 如果启用深度思考或全网搜索，添加工具参数
        if self.enable_deep_thinking or self.enable_web_search:
            api_params['parameters']['tools'] = []
            
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
        
        try:
            response = Generation.call(**api_params)
            
            if response.status_code == 200:
                # 从response中提取文本内容
                content = self._extract_content_from_response(response)
                
                logger.info(f"Qwen分析成功 - 股票: {stock_code}, 内容长度: {len(content)} 字符")
                
                return AnalysisResult(
                    success=True,
                    content=content,
                    provider='qwen',
                    model=self.model,
                    tokens_used=getattr(response.usage, 'total_tokens', None) if hasattr(response, 'usage') else None,
                    metadata={'response_status': response.status_code}
                )
            else:
                error_msg = getattr(response, 'message', f"HTTP {response.status_code}")
                logger.error(f"Qwen API请求失败 - 股票: {stock_code}, 错误: {error_msg}")
                
                error_type = self._classify_qwen_error(response.status_code)
                return AnalysisResult(
                    success=False,
                    error=f"Qwen API错误: {error_msg}",
                    error_type=error_type,
                    provider='qwen',
                    model=self.model
                )
                
        except Exception as e:
            logger.error(f"Qwen标准模型请求失败 - 股票: {stock_code}, 错误: {str(e)}")
            return AnalysisResult(
                success=False,
                error=str(e),
                error_type=ErrorType.UNKNOWN_ERROR,
                provider='qwen',
                model=self.model
            )
    
    def _handle_deep_research_model(self, formatted_prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """处理深度研究模型请求"""
        from dashscope import Generation
        
        stock_code = stock_info.get('code', 'unknown')
        
        # 直接使用用户传入的提示词，不进行任何修改
        # 这样用户可以完全控制分析的内容和方向
        logger.info(f"使用qwen-deep-research模型，直接使用用户提示词")
        
        api_params = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': formatted_prompt}],
            'stream': True,  # qwen-deep-research 目前仅支持流式输出
            'parameters': {
                'max_tokens': 15000,  # 大幅增加token限制，确保生成详细报告
                'temperature': 0.7
            }
        }
        
        try:
            # 使用支持反问确认的响应处理方法
            import time
            start_time = time.time()
            
            result = self._process_deep_research_response_with_confirmation(api_params, stock_code, 0)
            response_time = time.time() - start_time
            
            if result.get('success', False):
                logger.info(f"Qwen深度研究分析成功 - 股票: {stock_code}, 内容长度: {len(result.get('content', ''))} 字符")
                
                return AnalysisResult(
                    success=True,
                    content=result.get('content', ''),
                    provider='qwen',
                    model=self.model,
                    metadata={
                        'response_time': response_time,
                        'stream_mode': True,
                        'confirmation_used': result.get('confirmation_used', False)
                    }
                )
            else:
                error_msg = result.get('error', '未知错误')
                logger.error(f"Qwen深度研究分析失败 - 股票: {stock_code}, 错误: {error_msg}")
                
                return AnalysisResult(
                    success=False,
                    error=f"Qwen深度研究分析失败: {error_msg}",
                    error_type=ErrorType.UNKNOWN_ERROR,
                    provider='qwen',
                    model=self.model
                )
                
        except Exception as e:
            logger.error(f"Qwen深度研究模型请求失败 - 股票: {stock_code}, 错误: {str(e)}")
            return AnalysisResult(
                success=False,
                error=str(e),
                error_type=ErrorType.UNKNOWN_ERROR,
                provider='qwen',
                model=self.model
            )
    
    def _process_deep_research_stream(self, response, stock_code: str) -> str:
        """处理深度研究模型的流式响应"""
        try:
            logger.info(f"开始处理Qwen深度研究流式响应 - 股票: {stock_code}")
            
            current_phase = None
            phase_content = ""
            final_content = ""
            chunk_count = 0
            
            for response_chunk in response:
                chunk_count += 1
                
                # 检查响应状态码
                if hasattr(response_chunk, 'status_code') and response_chunk.status_code != 200:
                    logger.error(f"qwen-deep-research HTTP返回码：{response_chunk.status_code}")
                    if hasattr(response_chunk, 'code'):
                        logger.error(f"错误码：{response_chunk.code}")
                    if hasattr(response_chunk, 'message'):
                        logger.error(f"错误信息：{response_chunk.message}")
                    continue
                
                if hasattr(response_chunk, 'output') and response_chunk.output:
                    message = response_chunk.output.get('message', {})
                    phase = message.get('phase')
                    content = message.get('content', '')
                    status = message.get('status')
                    
                    # 阶段变化检测
                    if phase != current_phase:
                        if current_phase and phase_content:
                            logger.info(f"qwen-deep-research {current_phase} 阶段完成")
                        current_phase = phase
                        phase_content = ""
                        if phase:
                            logger.info(f"qwen-deep-research 进入 {phase} 阶段")
                    
                    # 累积阶段内容
                    if content:
                        phase_content += content
                        final_content += content
                        logger.debug(f"Chunk {chunk_count}: 累积内容长度: {len(final_content)} 字符, 当前内容: '{content}'")
            
            logger.info(f"Qwen深度研究流式响应处理完成 - 股票: {stock_code}, 处理了{chunk_count}个chunk, 总内容长度: {len(final_content)} 字符")
            
            if not final_content:
                logger.warning(f"Qwen深度研究流式响应为空 - 股票: {stock_code}")
                return "深度研究分析完成，但未获取到有效内容。"
            
            return final_content
            
        except Exception as e:
            logger.error(f"处理Qwen深度研究流式响应失败 - 股票: {stock_code}, 错误: {str(e)}")
            logger.error(f"错误详情: {str(e)}", exc_info=True)
            return f"深度研究分析完成，但处理响应时出现问题: {str(e)}"
    
    def _handle_max_preview_model(self, formatted_prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """处理qwen-max-preview模型请求"""
        from dashscope import Generation
        
        stock_code = stock_info.get('code', 'unknown')
        
        # 直接使用用户传入的提示词，不进行任何修改
        logger.info(f"使用qwen-max-preview模型，直接使用用户提示词")
        
        api_params = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': formatted_prompt}],
            'parameters': {
                'max_tokens': 32000,  # 使用更高的token限制
                'temperature': 0.7,
                'result_format': 'message'
            }
        }
        
        try:
            response = Generation.call(**api_params)
            
            if response.status_code == 200:
                # 从response中提取文本内容
                content = self._extract_content_from_response(response)
                
                logger.info(f"Qwen Max Preview分析成功 - 股票: {stock_code}, 内容长度: {len(content)} 字符")
                
                return AnalysisResult(
                    success=True,
                    content=content,
                    provider='qwen',
                    model=self.model,
                    tokens_used=getattr(response.usage, 'total_tokens', None) if hasattr(response, 'usage') else None,
                    metadata={'response_status': response.status_code, 'model_type': 'max_preview'}
                )
            else:
                error_msg = getattr(response, 'message', f"HTTP {response.status_code}")
                logger.error(f"Qwen Max Preview API请求失败 - 股票: {stock_code}, 错误: {error_msg}")
                
                error_type = self._classify_qwen_error(response.status_code)
                return AnalysisResult(
                    success=False,
                    error=f"Qwen Max Preview API错误: {error_msg}",
                    error_type=error_type,
                    provider='qwen',
                    model=self.model
                )
                
        except Exception as e:
            logger.error(f"Qwen Max Preview模型请求失败 - 股票: {stock_code}, 错误: {str(e)}")
            return AnalysisResult(
                success=False,
                error=str(e),
                error_type=ErrorType.UNKNOWN_ERROR,
                provider='qwen',
                model=self.model
            )
    
    def _extract_content_from_response(self, response) -> str:
        """从响应中提取内容"""
        try:
            if hasattr(response, 'output') and response.output:
                if hasattr(response.output, 'choices') and response.output.choices:
                    return response.output.choices[0].message.content
                elif hasattr(response.output, 'text') and response.output.text:
                    return response.output.text
                else:
                    return str(response.output)
            else:
                return str(response)
        except Exception as e:
            logger.error(f"解析Qwen响应失败: {str(e)}")
            return f"Qwen分析完成，但解析响应时出现问题: {str(e)}"
    
    def _classify_qwen_error(self, status_code: int) -> ErrorType:
        """根据Qwen API状态码分类错误类型"""
        if status_code == 401 or status_code == 403:
            return ErrorType.AUTHENTICATION_ERROR
        elif status_code == 429:
            return ErrorType.RATE_LIMIT_ERROR
        elif 400 <= status_code < 500:
            return ErrorType.API_ERROR
        elif 500 <= status_code < 600:
            return ErrorType.NETWORK_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def test_connection(self) -> bool:
        """测试Qwen连接"""
        try:
            from dashscope import Generation
            
            # 基础测试参数
            api_params = {
                'model': self.model,
                'prompt': "Hello",
                'parameters': {
                    'max_tokens': 10,
                    'result_format': 'message'
                }
            }
            
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
        # 深度思考和全网搜索相关配置
        self.enable_deep_thinking = config.get('enable_deep_thinking', True)
        self.enable_web_search = config.get('enable_web_search', True)
        self.thinking_steps = config.get('thinking_steps', 3)  # 思考步数
    
    def _make_api_request(self, prompt: str, stock_info: Dict[str, Any]) -> AnalysisResult:
        """执行DeepSeek API请求"""
        stock_code = stock_info.get('code', 'unknown')
        start_time = time.time()
        
        logger.info(f"调用DeepSeek API - 股票: {stock_code}, 模型: {self.model}")
        logger.debug(f"API URL: {self.api_url}")
        logger.debug(f"API密钥长度: {len(self.api_key) if self.api_key else 0}")
        
        # 格式化提示词
        formatted_prompt = self.format_prompt(prompt, stock_info)
        logger.debug(f"提示词长度: {len(formatted_prompt)} 字符")
        
        # 准备请求数据
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        # 基础请求数据 - 直接使用用户传入的提示词，不添加系统消息
        # 这样用户可以完全控制分析的内容和方向
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": formatted_prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        # 如果启用深度思考或全网搜索，添加工具参数（但deepseek-reasoner不支持工具调用）
        if self.model != 'deepseek-reasoner' and (self.enable_deep_thinking or self.enable_web_search):
            data['tools'] = []
            
            if self.enable_deep_thinking:
                data['tools'].append({
                    'type': 'function',
                    'function': {
                        'name': 'deep_thinking',
                        'description': '深度思考工具，用于多步推理分析',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'thinking_steps': {
                                    'type': 'integer',
                                    'description': f'思考步数，建议{self.thinking_steps}步'
                                }
                            }
                        }
                    }
                })
            
            if self.enable_web_search:
                data['tools'].append({
                    'type': 'function',
                    'function': {
                        'name': 'web_search',
                        'description': '全网搜索工具，用于获取最新信息',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'query': {
                                    'type': 'string',
                                    'description': '搜索关键词'
                                }
                            }
                        }
                    }
                })
        
        # 根据模型类型进行不同的处理
        if self.model == 'deepseek-reasoner':
            # DeepSeek Reasoner 模型专门用于推理，不需要额外提示
            logger.debug("使用DeepSeek Reasoner模型，专注于推理任务")
        elif self.enable_deep_thinking:
            # 其他模型如果启用深度思考，在用户消息前添加简短的提示
            data["messages"][0]["content"] = f"请深入思考，进行多步推理分析。\n\n{formatted_prompt}"
            logger.debug("DeepSeek Chat 使用深度思考模式，在用户提示词前添加深度思考提示")
        
        try:
            # 调用DeepSeek API，使用新的超时配置
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                timeout=(self.connect_timeout, self.request_timeout)
            )
            
            logger.debug(f"DeepSeek API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"DeepSeek API返回成功 - 股票: {stock_code}")
                
                message = result['choices'][0]['message']
                finish_reason = result['choices'][0].get('finish_reason', '')
                
                # 如果返回工具调用，需要继续对话获取最终结果
                if finish_reason == 'tool_calls' and 'tool_calls' in message:
                    logger.info("检测到工具调用，继续对话获取最终结果")
                    return self._continue_conversation_with_tools(data, message, headers, stock_code, start_time)
                
                content = self._extract_deepseek_content(message)
                
                logger.info(f"DeepSeek分析成功 - 股票: {stock_code}, 内容长度: {len(content)} 字符")
                
                return AnalysisResult(
                    success=True,
                    content=content,
                    provider='deepseek',
                    model=self.model,
                    tokens_used=result['usage']['total_tokens'] if 'usage' in result else None,
                    metadata={'response_status': response.status_code}
                )
            else:
                # 根据状态码分类错误
                error_type = self._classify_http_error(response.status_code)
                error_msg = f'DeepSeek API request failed: {response.status_code} - {response.text}'
                
                logger.error(f"DeepSeek API请求失败 - 股票: {stock_code}, 状态码: {response.status_code}")
                
                return AnalysisResult(
                    success=False,
                    error=error_msg,
                    error_type=error_type,
                    provider='deepseek',
                    model=self.model
                )
                
        except requests.exceptions.Timeout:
            logger.error(f"DeepSeek API请求超时 - 股票: {stock_code}")
            return AnalysisResult(
                success=False,
                error='Request timeout',
                error_type=ErrorType.TIMEOUT_ERROR,
                provider='deepseek',
                model=self.model
            )
        except requests.exceptions.ConnectionError as e:
            logger.error(f"DeepSeek API连接错误 - 股票: {stock_code}, 错误: {str(e)}")
            return AnalysisResult(
                success=False,
                error=f'Connection error: {str(e)}',
                error_type=ErrorType.NETWORK_ERROR,
                provider='deepseek',
                model=self.model
            )
        except Exception as e:
            logger.error(f"DeepSeek API请求异常 - 股票: {stock_code}, 错误: {str(e)}")
            return AnalysisResult(
                success=False,
                error=str(e),
                error_type=ErrorType.UNKNOWN_ERROR,
                provider='deepseek',
                model=self.model
            )
    
    def _extract_deepseek_content(self, message: Dict[str, Any]) -> str:
        """从DeepSeek响应中提取内容"""
        # 处理不同的响应格式
        if 'content' in message and message['content']:
            # 基础响应格式
            return message['content']
        elif 'reasoning_content' in message and message['reasoning_content']:
            # 推理内容格式
            return message['reasoning_content']
        elif 'tool_calls' in message and message['tool_calls']:
            # 工具调用格式 - 处理深度思考和搜索工具
            logger.info("检测到工具调用，处理深度思考结果")
            return self._process_tool_calls(message['tool_calls'])
        else:
            logger.warning(f"DeepSeek响应格式未知: {message}")
            return "响应格式异常，请检查API配置"
    
    def _process_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> str:
        """处理工具调用结果 - 需要继续对话获取最终结果"""
        try:
            # 收集工具调用信息
            tool_info = []
            for tool_call in tool_calls:
                if tool_call.get('type') == 'function':
                    function_name = tool_call.get('function', {}).get('name', '')
                    function_args = tool_call.get('function', {}).get('arguments', '{}')
                    
                    if function_name == 'deep_thinking':
                        try:
                            args = json.loads(function_args)
                            thinking_steps = args.get('thinking_steps', 3)
                            tool_info.append(f"深度思考（{thinking_steps}步推理）")
                        except json.JSONDecodeError:
                            tool_info.append("深度思考")
                    
                    elif function_name == 'web_search':
                        try:
                            args = json.loads(function_args)
                            query = args.get('query', '')
                            tool_info.append(f"网络搜索：{query}")
                        except json.JSONDecodeError:
                            tool_info.append("网络搜索")
                    
                    else:
                        tool_info.append(f"工具调用：{function_name}")
            
            # 返回工具调用信息，提示用户这是中间步骤
            if tool_info:
                return f"正在使用深度思考模式进行分析...\n\n已启用工具：{', '.join(tool_info)}\n\n请稍候，系统正在处理推理结果..."
            else:
                return "深度思考模式已启用，正在处理推理结果..."
                
        except Exception as e:
            logger.error(f"处理工具调用时出错: {str(e)}")
            return "深度思考分析进行中，请稍候..."
    
    def _continue_conversation_with_tools(self, original_data: Dict[str, Any], tool_message: Dict[str, Any], headers: Dict[str, str], stock_code: str, start_time: float) -> AnalysisResult:
        """继续对话以获取工具调用的最终结果"""
        try:
            # 计算响应时间
            response_time = time.time() - start_time
            # 构建继续对话的请求
            continue_data = {
                "model": original_data["model"],
                "messages": original_data["messages"] + [
                    tool_message,  # 添加工具调用消息
                    {
                        "role": "tool",
                        "content": "工具调用已完成，请提供最终的分析结果。",
                        "tool_call_id": tool_message["tool_calls"][0]["id"] if tool_message.get("tool_calls") else None
                    }
                ],
                "max_tokens": original_data["max_tokens"],
                "temperature": original_data["temperature"]
            }
            
            logger.info(f"继续对话获取最终结果 - 股票: {stock_code}")
            
            # 发送继续对话请求
            response = requests.post(
                self.api_url,
                headers=headers,
                json=continue_data,
                timeout=(self.connect_timeout, self.request_timeout)
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']
                content = self._extract_deepseek_content(message)
                
                logger.info(f"DeepSeek深度思考分析完成 - 股票: {stock_code}, 内容长度: {len(content)} 字符")
                
                return AnalysisResult(
                    success=True,
                    content=content,
                    provider='deepseek',
                    model=self.model,
                    tokens_used=result['usage']['total_tokens'] if 'usage' in result else None,
                    response_time=response_time,
                    metadata={'response_status': response.status_code, 'deep_thinking': True}
                )
            else:
                logger.error(f"继续对话失败: {response.status_code} - {response.text}")
                return AnalysisResult(
                    success=False,
                    error=f'Continue conversation failed: {response.status_code}',
                    error_type=ErrorType.API_ERROR,
                    provider='deepseek',
                    model=self.model
                )
                
        except Exception as e:
            logger.error(f"继续对话时出错: {str(e)}")
            return AnalysisResult(
                success=False,
                error=f'Continue conversation error: {str(e)}',
                error_type=ErrorType.UNKNOWN_ERROR,
                provider='deepseek',
                model=self.model
            )
    
    def _classify_http_error(self, status_code: int) -> ErrorType:
        """根据HTTP状态码分类错误类型"""
        if status_code == 401 or status_code == 403:
            return ErrorType.AUTHENTICATION_ERROR
        elif status_code == 429:
            return ErrorType.RATE_LIMIT_ERROR
        elif 400 <= status_code < 500:
            return ErrorType.API_ERROR
        elif 500 <= status_code < 600:
            return ErrorType.NETWORK_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def test_connection(self) -> bool:
        """测试DeepSeek连接"""
        try:
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
            
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                timeout=(self.connect_timeout, 30)  # 测试连接使用较短的超时时间
            )
            
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
    def create_provider_from_db_config(config_id: int) -> LLMProvider:
        """从数据库配置创建Provider实例"""
        try:
            from app import db
            from app.models.ai_config import AIConfig
            
            config = AIConfig.query.get(config_id)
            if not config:
                raise ValueError(f"配置不存在: {config_id}")
            
            if not config.is_active:
                raise ValueError(f"配置未激活: {config.provider_name}")
            
            return LLMProviderFactory.create_provider(
                config.provider_name, 
                config.get_config_dict()
            )
        except Exception as e:
            logger.error(f"从数据库配置创建Provider失败: {str(e)}")
            raise
    
    @staticmethod
    def create_default_provider() -> LLMProvider:
        """创建默认Provider实例"""
        try:
            from app import db
            from app.models.ai_config import AIConfig
            
            # 获取默认配置
            default_config = AIConfig.query.filter_by(is_default=True, is_active=True).first()
            if not default_config:
                # 如果没有默认配置，获取第一个激活的配置
                default_config = AIConfig.query.filter_by(is_active=True).first()
            
            if not default_config:
                raise ValueError("没有可用的AI配置")
            
            return LLMProviderFactory.create_provider(
                default_config.provider_name,
                default_config.get_config_dict()
            )
        except Exception as e:
            logger.error(f"创建默认Provider失败: {str(e)}")
            raise
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """获取可用的Provider列表"""
        return ['qwen', 'deepseek', 'gemini', 'openai']
    
    @staticmethod
    def get_available_models(provider: str) -> Dict[str, Dict[str, Any]]:
        """获取指定Provider的可用模型列表"""
        models = {
            'qwen': {
                'qwen-turbo': {
                    'name': 'Qwen Turbo',
                    'description': '快速响应模型，适合一般对话和分析任务',
                    'cost_level': 'low',
                    'response_time': 'fast',
                    'max_tokens': 8000,
                    'features': ['基础对话', '简单分析']
                },
                'qwen-plus': {
                    'name': 'Qwen Plus',
                    'description': '平衡性能和成本的模型，适合大多数分析任务',
                    'cost_level': 'medium',
                    'response_time': 'medium',
                    'max_tokens': 32000,
                    'features': ['深度分析', '代码生成', '数学推理']
                },
                'qwen-max': {
                    'name': 'Qwen Max',
                    'description': '高性能模型，适合复杂分析和专业任务',
                    'cost_level': 'high',
                    'response_time': 'slow',
                    'max_tokens': 32000,
                    'features': ['复杂推理', '专业分析', '多轮对话']
                },
                'qwen-deep-research': {
                    'name': 'Qwen Deep Research',
                    'description': '深度研究模型，支持流式输出和深度思考，适合专业研究',
                    'cost_level': 'very_high',
                    'response_time': 'very_slow',
                    'max_tokens': 15000,
                    'features': ['深度研究', '流式输出', '专业分析'],
                    'warning': '此模型成本较高，响应时间较长，适合专业研究场景'
                },
                'qwen-max-preview': {
                    'name': 'Qwen Max Preview',
                    'description': '最新预览模型，具有最强的分析能力',
                    'cost_level': 'very_high',
                    'response_time': 'slow',
                    'max_tokens': 32000,
                    'features': ['最新技术', '最强性能', '复杂推理'],
                    'warning': '此模型成本最高，适合对分析质量要求极高的场景'
                }
            },
            'deepseek': {
                'deepseek-chat': {
                    'name': 'DeepSeek Chat',
                    'description': '通用对话模型，适合日常分析和对话任务',
                    'cost_level': 'medium',
                    'response_time': 'medium',
                    'max_tokens': 32000,
                    'features': ['通用对话', '代码生成', '数学推理']
                },
                'deepseek-reasoner': {
                    'name': 'DeepSeek Reasoner',
                    'description': '推理专用模型，具有强大的逻辑推理能力',
                    'cost_level': 'high',
                    'response_time': 'slow',
                    'max_tokens': 32000,
                    'features': ['深度推理', '逻辑分析', '复杂问题解决'],
                    'warning': '此模型专注于推理任务，成本较高但推理能力更强'
                }
            },
            'gemini': {
                'gemini-2.0-flash': {
                    'name': 'Gemini 2.0 Flash',
                    'description': 'Google最新模型，快速响应，适合各种分析任务',
                    'cost_level': 'low',
                    'response_time': 'fast',
                    'max_tokens': 32000,
                    'features': ['快速响应', '多模态', '多语言']
                }
            }
        }
        
        return models.get(provider.lower(), {})
    
    @staticmethod
    def test_provider(provider_type: str, config: Dict[str, Any]) -> bool:
        """测试Provider连接"""
        try:
            provider = LLMProviderFactory.create_provider(provider_type, config)
            return provider.test_connection()
        except Exception as e:
            logger.error(f"测试Provider失败: {str(e)}")
            return False
