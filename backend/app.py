#!/usr/bin/env python3
"""
智策股析 - 应用启动入口
"""
import os
import sys

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')

# 创建Flask应用实例 - 避免循环导入
def create_app_instance():
    """创建Flask应用实例"""
    from app import create_app
    return create_app(os.getenv('FLASK_ENV', 'production'))

# 创建应用实例
app = create_app_instance()

# 确保app对象可以被gunicorn找到
__all__ = ['app']

# 延迟导入模型，避免循环导入
def get_models():
    from app.models import (
        User, UserPlan, Stock, UserWatchlist, AnalysisTask, 
        PromptTemplate, ReportIndex, EmailSubscription, 
        PaymentTransaction, Admin, SystemConfig
    )
    return {
        'User': User,
        'UserPlan': UserPlan,
        'Stock': Stock,
        'UserWatchlist': UserWatchlist,
        'AnalysisTask': AnalysisTask,
        'PromptTemplate': PromptTemplate,
        'ReportIndex': ReportIndex,
        'EmailSubscription': EmailSubscription,
        'PaymentTransaction': PaymentTransaction,
        'Admin': Admin,
        'SystemConfig': SystemConfig,
    }

@app.shell_context_processor
def make_shell_context():
    """Flask shell上下文"""
    from app import db
    models = get_models()
    return {
        'db': db,
        'app': app,
        **models
    }

@app.cli.command()
def init_db():
    """初始化数据库"""
    from app import db
    from app.services.data.database_service import DatabaseService
    
    with app.app_context():
        db_service = DatabaseService(db.session)
        db_service.initialize_database()
    
    print("数据库初始化完成!")

@app.cli.command() 
def seed_db():
    """填充初始数据"""
    from app import db
    from app.services.data.database_service import DatabaseService
    
    with app.app_context():
        db_service = DatabaseService(db.session)
        db_service.populate_stock_pools()
    
    print("初始数据填充完成!")

@app.cli.command()
def reset_db():
    """重置数据库（危险操作）"""
    import click
    from app import db
    from app.services.data.database_service import DatabaseService
    
    if click.confirm('确定要重置数据库吗？这将删除所有数据！'):
        with app.app_context():
            db_service = DatabaseService(db.session)
            db_service.reset_database()
        
        print("数据库重置完成!")
    else:
        print("操作已取消")

if __name__ == '__main__':
    # 开发环境启动
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=True,
        threaded=True
    )
