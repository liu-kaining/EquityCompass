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
    print("正在创建数据库表...")
    db.create_all()
    print("数据库初始化完成!")

@app.cli.command() 
def seed_db():
    """填充初始数据"""
    print("正在填充初始数据...")
    
    # 这里添加初始数据填充逻辑
    # 例如：内置股票池数据
    
    print("初始数据填充完成!")

if __name__ == '__main__':
    # 开发环境启动
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
