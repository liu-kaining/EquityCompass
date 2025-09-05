#!/usr/bin/env python3
"""
创建测试统计数据
"""
import os
import sys
import json
from datetime import datetime, date, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.analysis import ReportIndex, ReportStatistics, ReportViewLog, ReportDownloadLog
from app.models.stock import Stock
from app.models.user import User

def create_test_data():
    """创建测试数据"""
    app = create_app()
    
    with app.app_context():
        print("🚀 开始创建测试统计数据...")
        
        # 1. 创建测试用户
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User(
                email='test@example.com',
                nickname='测试用户',
                is_active=True
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ 创建测试用户")
        else:
            print("ℹ️  测试用户已存在")
        
        # 2. 获取或创建测试股票
        test_stock = Stock.query.filter_by(code='AAPL').first()
        if not test_stock:
            test_stock = Stock(
                code='AAPL',
                name='苹果公司',
                market='US',
                exchange='NASDAQ',
                industry='科技',
                stock_type='BUILT_IN'
            )
            db.session.add(test_stock)
            db.session.commit()
            print("✅ 创建测试股票")
        else:
            print("ℹ️  测试股票已存在")
        
        # 3. 创建测试报告
        test_reports = []
        for i in range(3):
            report_date = date.today() - timedelta(days=i)
            
            # 检查是否已存在报告
            existing_report = ReportIndex.query.filter_by(
                stock_id=test_stock.id,
                analysis_date=report_date
            ).first()
            
            if not existing_report:
                report = ReportIndex(
                    stock_id=test_stock.id,
                    analysis_date=report_date,
                    file_path=f'data/reports/{report_date}/AAPL_test_{i}.json',
                    summary=f'苹果公司第{i+1}次测试分析报告',
                    generated_at=datetime.utcnow() - timedelta(days=i)
                )
                db.session.add(report)
                db.session.commit()
                test_reports.append(report)
                print(f"✅ 创建测试报告 {i+1}")
            else:
                test_reports.append(existing_report)
                print(f"ℹ️  测试报告 {i+1} 已存在")
        
        # 4. 为每个报告创建统计数据
        for i, report in enumerate(test_reports):
            # 检查是否已有统计数据
            existing_stats = ReportStatistics.query.filter_by(report_id=report.id).first()
            
            if not existing_stats:
                # 创建统计数据
                stats = ReportStatistics(
                    report_id=report.id,
                    view_count=10 + i * 5,  # 10, 15, 20
                    download_count=2 + i,   # 2, 3, 4
                    favorite_count=i,       # 0, 1, 2
                    last_viewed_at=datetime.utcnow() - timedelta(hours=i),
                    last_downloaded_at=datetime.utcnow() - timedelta(hours=i*2)
                )
                db.session.add(stats)
                print(f"✅ 创建报告 {i+1} 统计数据")
            else:
                print(f"ℹ️  报告 {i+1} 统计数据已存在")
        
        # 5. 创建浏览日志
        for i, report in enumerate(test_reports):
            # 为每个报告创建几条浏览日志
            for j in range(3):
                view_log = ReportViewLog(
                    report_id=report.id,
                    user_id=test_user.id if j < 2 else None,  # 有些是匿名浏览
                    ip_address=f'192.168.1.{100 + j}',
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    referer='https://example.com',
                    view_duration=30 + j * 10,  # 30, 40, 50秒
                    created_at=datetime.utcnow() - timedelta(hours=i*3 + j)
                )
                db.session.add(view_log)
            print(f"✅ 创建报告 {i+1} 浏览日志")
        
        # 6. 创建下载日志
        for i, report in enumerate(test_reports):
            # 为每个报告创建几条下载日志
            for j in range(2):
                download_log = ReportDownloadLog(
                    report_id=report.id,
                    user_id=test_user.id,
                    ip_address=f'192.168.1.{200 + j}',
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    download_format='PDF',
                    file_size=1024 * 1024 * (2 + j),  # 2MB, 3MB
                    created_at=datetime.utcnow() - timedelta(hours=i*2 + j)
                )
                db.session.add(download_log)
            print(f"✅ 创建报告 {i+1} 下载日志")
        
        # 提交所有更改
        db.session.commit()
        
        print("\n🎉 测试数据创建完成！")
        
        # 显示统计信息
        print("\n📊 数据统计:")
        print(f"用户数量: {User.query.count()}")
        print(f"股票数量: {Stock.query.count()}")
        print(f"报告数量: {ReportIndex.query.count()}")
        print(f"统计记录数量: {ReportStatistics.query.count()}")
        print(f"浏览日志数量: {ReportViewLog.query.count()}")
        print(f"下载日志数量: {ReportDownloadLog.query.count()}")
        
        return True

if __name__ == "__main__":
    try:
        create_test_data()
    except Exception as e:
        print(f"❌ 创建测试数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
