#!/usr/bin/env python3
"""
添加报告统计表的数据库迁移脚本
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.analysis import ReportStatistics, ReportViewLog, ReportDownloadLog

def add_statistics_tables():
    """添加报告统计表"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始创建报告统计表...")
            
            # 创建表
            db.create_all()
            
            print("✅ 报告统计表创建成功！")
            print("已创建的表：")
            print("  - report_statistics (报告统计表)")
            print("  - report_view_logs (报告浏览日志表)")
            print("  - report_download_logs (报告下载日志表)")
            
            # 为现有报告创建统计记录
            print("\n开始为现有报告创建统计记录...")
            
            from app.models.analysis import ReportIndex
            from sqlalchemy import text
            
            # 获取所有现有报告
            reports = ReportIndex.query.all()
            
            for report in reports:
                # 检查是否已有统计记录
                existing_stats = ReportStatistics.query.filter_by(report_id=report.id).first()
                if not existing_stats:
                    # 创建新的统计记录
                    stats = ReportStatistics(report_id=report.id)
                    db.session.add(stats)
                    print(f"  - 为报告 {report.id} 创建统计记录")
            
            db.session.commit()
            print(f"✅ 为 {len(reports)} 个报告创建了统计记录")
            
        except Exception as e:
            print(f"❌ 创建表失败: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 开始添加报告统计表...")
    success = add_statistics_tables()
    
    if success:
        print("\n🎉 数据库迁移完成！")
    else:
        print("\n❌ 数据库迁移失败！")
        sys.exit(1)
