"""
EquityCompass Core - 可复用的核心功能模块

这个包提供了以下核心功能：
- 用户认证系统 (JWT, 验证码, 权限管理)
- AI 代理系统 (多模型支持, 重试机制)
- 异步任务管理 (任务生命周期, 状态跟踪)
- 前端 UI 组件 (Markdown 渲染, 弹窗组件)
- 数据层抽象 (Repository 模式, Service 层)
"""

__version__ = "1.0.0"
__author__ = "EquityCompass Team"
__email__ = "team@equitycompass.com"

# 导入核心模块
from .auth import AuthService, JWTService, VerificationService
from .ai import LLMProvider, TaskManager, AnalysisService
from .ui import MarkdownRenderer, ConfirmModal, UIUtils
from .data import Repository, Service

# 导出主要类和函数
__all__ = [
    # 认证相关
    "AuthService",
    "JWTService", 
    "VerificationService",
    
    # AI 相关
    "LLMProvider",
    "TaskManager",
    "AnalysisService",
    
    # UI 相关
    "MarkdownRenderer",
    "ConfirmModal",
    "UIUtils",
    
    # 数据相关
    "Repository",
    "Service",
]

# 配置默认设置
DEFAULT_CONFIG = {
    "auth": {
        "jwt_secret": "your-secret-key",
        "jwt_expiry": 3600,
        "verification_code_ttl": 600,
        "max_login_attempts": 5,
    },
    "ai": {
        "providers": ["qwen", "deepseek", "openai"],
        "default_provider": "qwen",
        "retry_config": {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 60.0,
            "exponential_base": 2.0,
        },
        "timeout_config": {
            "request_timeout": 120,
            "connect_timeout": 30,
        },
    },
    "ui": {
        "markdown_extensions": ["codehilite", "fenced_code", "tables"],
        "modal_theme": "default",
        "responsive_breakpoints": {
            "sm": 576,
            "md": 768,
            "lg": 992,
            "xl": 1200,
        },
    },
    "data": {
        "default_page_size": 20,
        "max_page_size": 100,
        "cache_ttl": 300,
    },
}

def get_config():
    """获取默认配置"""
    return DEFAULT_CONFIG.copy()

def configure(**kwargs):
    """配置模块设置"""
    global DEFAULT_CONFIG
    for key, value in kwargs.items():
        if key in DEFAULT_CONFIG:
            DEFAULT_CONFIG[key].update(value)
        else:
            DEFAULT_CONFIG[key] = value
