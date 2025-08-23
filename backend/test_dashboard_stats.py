#!/usr/bin/env python3
"""
测试仪表板统计数据
"""
from app import create_app, db
from app.models.user import User
from app.services.data.stock_service import StockDataService
from app.services.ai.analysis_service import AnalysisService

def test_dashboard_stats():
    app = create_app()
    with app.app_context():
        print("=== 测试仪表板统计数据 ===")
        
        # 获取用户
        user = User.query.filter_by(email='liqian_macmini@qxmy.tech').first()
        if not user:
            print("❌ 没有找到用户")
            return
        
        print(f"✅ 找到用户: {user.email} (ID: {user.id})")
        
        # 获取服务
        stock_service = StockDataService(db.session)
        analysis_service = AnalysisService(db.session)
        
        # 获取关注列表数量
        watchlist_data = stock_service.get_user_watchlist(user.id)
        watchlist_count = watchlist_data['count']
        
        print(f"\n📊 关注列表统计:")
        print(f"   关注股票数量: {watchlist_count}")
        print(f"   最大关注数: {watchlist_data['max_count']}")
        print(f"   剩余额度: {watchlist_data['remaining_slots']}")
        
        # 获取报告数量
        reports = analysis_service.get_user_reports(user.id, limit=100)
        reports_count = len(reports)
        
        print(f"\n📄 分析报告统计:")
        print(f"   报告数量: {reports_count}")
        
        if reports_count > 0:
            print("   最近的报告:")
            for i, report in enumerate(reports[:3]):
                print(f"     {i+1}. {report.get('stock_code', 'Unknown')} - {report.get('analysis_date', 'Unknown')}")
        
        # 显示关注列表详情
        print(f"\n📋 关注列表详情:")
        for item in watchlist_data['watchlist']:
            print(f"   - {item['stock']['code']}: {item['stock']['name']} (添加时间: {item['added_at']})")
        
        print(f"\n✅ 统计数据验证完成！")
        print(f"   仪表板应显示: 关注股票 {watchlist_count}, 分析报告 {reports_count}")

if __name__ == "__main__":
    test_dashboard_stats()
