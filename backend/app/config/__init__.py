"""
配置包
"""
from .settings import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from .prompts import PROMPT_CONFIG

__all__ = ['Config', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig', 'PROMPT_CONFIG']
