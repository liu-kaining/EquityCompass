#!/usr/bin/env python3
"""
检查现有数据
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.analysis import ReportIndex, ReportStatistics, ReportViewLog, ReportDownloadLog
from app.models.stock import Stock
from app.models.user import User

def check_data():
    """检查现有数据"""
    app = create_app()
    
    with app.app_context():
        print("🔍 检查现有数据...")
        
        # 检查用户
        users = User.query.all()
        print(f"👥 用户数量: {len(users)}")
        for user in users:
            print(f"   - {user.email} (ID: {user.id})")
        
        # 检查股票
        stocks = Stock.query.all()
        print(f"📈 股票数量: {len(stocks)}")
        for stock in stocks[:5]:  # 只显示前5个
            print(f"   - {stock.name} ({stock.code})")
        
        # 检查报告
        reports = ReportIndex.query.all()
        print(f"📄 报告数量: {len(reports)}")
        for report in reports:
            print(f"   - {report.stock.name} ({report.stock.code}) - {report.analysis_date}")
        
        # 检查统计记录
        stats = ReportStatistics.query.all()
        print(f"📊 统计记录数量: {len(stats)}")
        
        # 检查浏览日志
        view_logs = ReportViewLog.query.all()
        print(f"👁️ 浏览日志数量: {len(view_logs)}")
        
        # 检查下载日志
        download_logs = ReportDownloadLog.query.all()
        print(f"📥 下载日志数量: {len(download_logs)}")
        
        # 检查报告文件
        import os
        reports_dir = 'data/reports'
        if os.path.exists(reports_dir):
            print(f"📁 报告文件目录存在: {reports_dir}")
            for root, dirs, files in os.walk(reports_dir):
                for file in files:
                    if file.endswith('.json'):
                        print(f"   - {os.path.join(root, file)}")
        else:
            print(f"❌ 报告文件目录不存在: {reports_dir}")

if __name__ == "__main__":
    check_data()
