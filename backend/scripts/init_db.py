#!/usr/bin/env python3
"""
数据库初始化脚本
用于手动初始化数据库表结构
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.services.data.database_service import DatabaseService

def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    # 创建应用上下文
    app = create_app(os.getenv("FLASK_ENV", "production"))
    
    with app.app_context():
        try:
            # 确保所有模型都被导入
            from app.models import (
                User, UserPlan, Stock, UserWatchlist, AnalysisTask, 
                PromptTemplate, ReportIndex, EmailSubscription, 
                PaymentTransaction, Admin, SystemConfig
            )
            print("✅ 模型导入完成")
            
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建完成")
            
            # 初始化基础数据
            db_service = DatabaseService(db.session)
            db_service.initialize_database()
            print("✅ 基础数据初始化完成")
            
            print("🎉 数据库初始化成功！")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    init_database()
