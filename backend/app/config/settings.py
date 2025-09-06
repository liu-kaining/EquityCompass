"""
应用配置设置
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置类"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///equitycompass.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1小时
    
    # 邮件配置
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    
    # AI分析配置
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    QWEN_API_KEY = os.getenv('QWEN_API_KEY') 
    
    # 数据存储路径
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
    STOCKS_DATA_FILE = os.path.join(DATA_DIR, 'stocks.json')
    
    # 分页配置
    STOCKS_PER_PAGE = 20
    REPORTS_PER_PAGE = 10
    
    # 用户限制
    MAX_WATCHLIST_SIZE = 20
    
    # 管理员配置
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@equitycompass.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123456')
    ADMIN_NICKNAME = os.getenv('ADMIN_NICKNAME', '系统管理员')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # 设为True可查看SQL语句


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
