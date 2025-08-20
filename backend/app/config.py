"""
智策股析 - 应用配置
"""
import os
from datetime import timedelta


class Config:
    """基础配置"""
    # 基本配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Session配置
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_NAME = 'equitycompass_session'
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-in-production')
    
    # 邮件配置
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@equitycompass.com')
    FROM_NAME = os.getenv('FROM_NAME', '智策股析')
    SEND_EMAIL = os.getenv('SEND_EMAIL', 'True').lower() == 'true'
    
    # 文件存储配置
    REPORTS_DIR = os.getenv('REPORTS_DIR', 'data/reports')
    EXPORTS_DIR = os.getenv('EXPORTS_DIR', 'data/exports')
    LOGS_DIR = os.getenv('LOGS_DIR', 'data/logs')
    
    # LLM API配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    QWEN_API_KEY = os.getenv('QWEN_API_KEY')
    
    # 支付网关配置
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    # 金融数据API配置
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 业务配置
    MAX_WATCHLIST_SIZE = 20
    VERIFICATION_CODE_EXPIRE = 600  # 10分钟
    RATE_LIMIT_PER_MINUTE = 60


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    
    # 开发环境数据库
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///dev.db'  # 直接在backend目录下
    )
    
    # 开发环境邮件配置 - 控制台输出
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = True
    
    # 开发环境日志级别
    LOG_LEVEL = 'DEBUG'
    
    # 开发环境允许的主机
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境数据库
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost/equitycompass'
    )
    
    # 生产环境日志级别
    LOG_LEVEL = 'INFO'
    
    # 生产环境安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 生产环境CORS配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    
    # 测试环境数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 测试环境不发送邮件
    MAIL_SUPPRESS_SEND = True
    
    # 测试环境JWT配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    
    # 测试环境Redis配置
    REDIS_URL = 'redis://localhost:6379/15'  # 使用不同的数据库


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
