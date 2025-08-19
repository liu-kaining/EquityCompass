#!/usr/bin/env python3
"""
智策股析 - 应用启动入口
"""
import os
from app import create_app, db
from app.models import (
    User, UserPlan, Stock, UserWatchlist, AnalysisTask, 
    PromptTemplate, ReportIndex, EmailSubscription, 
    PaymentTransaction, Admin, SystemConfig
)

# 创建Flask应用
app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Flask shell上下文"""
    return {
        'db': db,
        'app': app,
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

@app.cli.command()
def init_db():
    """初始化数据库"""
    from app.services.data.database_service import DatabaseService
    
    with app.app_context():
        db_service = DatabaseService(db.session)
        db_service.initialize_database()
    
    print("数据库初始化完成!")

@app.cli.command() 
def seed_db():
    """填充初始数据"""
    from app.services.data.database_service import DatabaseService
    
    with app.app_context():
        db_service = DatabaseService(db.session)
        db_service.populate_stock_pools()
    
    print("初始数据填充完成!")

@app.cli.command()
def reset_db():
    """重置数据库（危险操作）"""
    import click
    
    if click.confirm('确定要重置数据库吗？这将删除所有数据！'):
        from app.services.data.database_service import DatabaseService
        
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
        port=5001,  # 改为5001端口避免冲突
        debug=True,
        threaded=True
    )
