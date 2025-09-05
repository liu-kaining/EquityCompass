#!/usr/bin/env python3
"""
重新创建数据库表
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.analysis import ReportIndex, ReportStatistics, ReportViewLog, ReportDownloadLog

def recreate_tables():
    """重新创建数据库表"""
    app = create_app()
    
    with app.app_context():
        print("🗑️ 删除现有表...")
        
        # 删除现有表（按依赖顺序）
        try:
            ReportDownloadLog.__table__.drop(db.engine, checkfirst=True)
            ReportViewLog.__table__.drop(db.engine, checkfirst=True)
            ReportStatistics.__table__.drop(db.engine, checkfirst=True)
            ReportIndex.__table__.drop(db.engine, checkfirst=True)
            print("✅ 现有表删除成功")
        except Exception as e:
            print(f"⚠️ 删除表时出错: {e}")
        
        print("\n🏗️ 重新创建表...")
        
        # 重新创建表
        try:
            db.create_all()
            print("✅ 表创建成功")
            
            # 验证表是否创建成功
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['report_index', 'report_statistics', 'report_view_logs', 'report_download_logs']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ 表 {table} 创建成功")
                else:
                    print(f"❌ 表 {table} 创建失败")
                    
        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 开始重新创建数据库表...")
    success = recreate_tables()
    
    if success:
        print("\n🎉 数据库表重新创建完成！")
    else:
        print("\n❌ 数据库表重新创建失败！")
        sys.exit(1)
