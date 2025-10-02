"""
智策股析 - Flask应用工厂
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 全局扩展对象
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
login_manager = LoginManager()





def create_app(config_name='development'):
    """Flask应用工厂函数"""
    # 确保环境变量已加载
    load_dotenv()
    
    app = Flask(__name__)
    
    # 配置日志
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # 输出到控制台
            logging.FileHandler('app.log', encoding='utf-8')  # 输出到文件
        ]
    )
    
    # 加载配置
    from app import config as config_module
    
    if config_name == 'development':
        app.config.from_object(config_module.DevelopmentConfig)
    elif config_name == 'production':
        app.config.from_object(config_module.ProductionConfig)
    elif config_name == 'testing':
        app.config.from_object(config_module.TestingConfig)
    else:
        app.config.from_object(config_module.DevelopmentConfig)
    
    # 配置session
    app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境设为False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, supports_credentials=True)
    jwt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    
    # 配置LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'info'
    
    # 用户加载器
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # 导入所有模型以确保表被创建
    from app.models import (
        User, UserPlan, Stock, UserWatchlist, AnalysisTask, 
        PromptTemplate, ReportIndex, ReportStatistics, ReportViewLog, ReportDownloadLog,
        EmailSubscription, PaymentTransaction, Admin, SystemConfig
    )
    
    # 导入金币系统模型
    from app.models.coin import UserCoin, CoinTransaction, CoinPackage, CoinOrder, DailyBonus
    
    # 注册Web页面蓝图
    from app.views.main import main_bp
    from app.views.auth import auth_bp
    from app.views.dashboard import dashboard_bp
    from app.views.analysis import analysis_bp
    from app.views.reports import reports_bp
    from app.views.stocks import stocks_bp
    from app.views.admin import admin_bp
    from app.views.ai_config import ai_config_bp
    from app.views.prompt import prompt_bp
    from app.views.coin import coin_bp
    
    # 注册API蓝图
    from app.api.auth_api import auth_api_bp
    from app.api.stocks_api import stocks_api_bp
    from app.api.analysis_api import analysis_api_bp
    from app.api.health import health_bp
    from app.api.report_statistics_api import report_statistics_bp
    from app.api.ai_config_api import ai_config_api_bp
    from app.api.prompt_api import prompt_api_bp
    from app.api.models_api import models_bp
    from app.api.coin_api import coin_bp as coin_api_bp
    
    # Web页面路由
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(stocks_bp, url_prefix='/stocks')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ai_config_bp, url_prefix='/admin')
    app.register_blueprint(prompt_bp, url_prefix='/admin')
    app.register_blueprint(coin_bp)
    
    # API路由 (保留一些API供Ajax使用)
    app.register_blueprint(auth_api_bp, url_prefix='/api/auth')
    app.register_blueprint(stocks_api_bp, url_prefix='/api/stocks')
    app.register_blueprint(analysis_api_bp, url_prefix='/api/analysis')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(report_statistics_bp, url_prefix='/api/report-statistics')
    app.register_blueprint(ai_config_api_bp, url_prefix='/api/ai-config')
    app.register_blueprint(prompt_api_bp, url_prefix='/api/prompt')
    app.register_blueprint(models_bp)
    app.register_blueprint(coin_api_bp, url_prefix='/api/coin', name='coin_api')
    

    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'NOT_FOUND', 'message': '资源不存在'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'success': False, 'error': 'INTERNAL_ERROR', 'message': '服务器内部错误'}, 500
    

    
    return app

# 为gunicorn创建应用实例
def create_app_for_gunicorn():
    """为gunicorn创建应用实例"""
    return create_app('production')

# 导出应用实例供gunicorn使用
app = create_app_for_gunicorn()
