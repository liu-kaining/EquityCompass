"""
智策股析 - Flask应用工厂
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from celery import Celery
import redis
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 全局扩展对象
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
redis_client = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))


def make_celery(app):
    """创建Celery实例"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(config_name='development'):
    """Flask应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    if config_name == 'development':
        app.config.from_object('app.config.DevelopmentConfig')
    elif config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # 注册蓝图
    from app.api.auth import auth_bp
    from app.api.users import users_bp
    from app.api.stocks import stocks_bp
    from app.api.watchlist import watchlist_bp
    from app.api.analysis import analysis_bp
    from app.api.reports import reports_bp
    from app.api.payment import payment_bp
    from app.api.email import email_bp
    from app.api.admin import admin_bp
    from app.api.health import health_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(stocks_bp, url_prefix='/api/stocks')
    app.register_blueprint(watchlist_bp, url_prefix='/api/watchlist')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')
    app.register_blueprint(email_bp, url_prefix='/api/email')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    
    # 创建Celery实例
    celery = make_celery(app)
    app.celery = celery
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'NOT_FOUND', 'message': '资源不存在'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'success': False, 'error': 'INTERNAL_ERROR', 'message': '服务器内部错误'}, 500
    
    # 健康检查
    @app.route('/')
    def index():
        return {'success': True, 'message': '智策股析 API 服务正常运行'}
    
    return app
