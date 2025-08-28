"""
智策股析 - Flask应用工厂
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 全局扩展对象
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()





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
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # 导入所有模型以确保表被创建
    from app.models import (
        User, UserPlan, Stock, UserWatchlist, AnalysisTask, 
        PromptTemplate, ReportIndex, ReportStatistics, ReportViewLog, ReportDownloadLog,
        EmailSubscription, PaymentTransaction, Admin, SystemConfig
    )
    
    # 注册Web页面蓝图
    from app.views.main import main_bp
    from app.views.auth import auth_bp
    from app.views.dashboard import dashboard_bp
    from app.views.analysis import analysis_bp
    from app.views.reports import reports_bp
    from app.views.stocks import stocks_bp
    
    # 注册API蓝图
    from app.api.auth_api import auth_api_bp
    from app.api.stocks_api import stocks_api_bp
    from app.api.analysis_api import analysis_api_bp
    from app.api.health import health_bp
    from app.api.report_statistics_api import report_statistics_bp
    
    # Web页面路由
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(stocks_bp, url_prefix='/stocks')
    
    # API路由 (保留一些API供Ajax使用)
    app.register_blueprint(auth_api_bp, url_prefix='/api/auth')
    app.register_blueprint(stocks_api_bp, url_prefix='/api/stocks')
    app.register_blueprint(analysis_api_bp, url_prefix='/api/analysis')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(report_statistics_bp, url_prefix='/api/report-statistics')
    

    
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
