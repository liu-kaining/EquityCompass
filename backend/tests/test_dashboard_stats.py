#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仪表板统计数据测试
验证用户关注列表和分析报告的统计数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.services.data.stock_service import StockDataService
from app.services.ai.analysis_service import AnalysisService

def test_dashboard_stats():
    """测试仪表板统计数据"""
    print("=== 测试仪表板统计数据 ===")
    
    app = create_app()
    with app.app_context():
        # 查找测试用户
        user_email = "liqian_macmini@qxmy.tech"
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            print(f"❌ 未找到用户: {user_email}")
            return
        
        print(f"✅ 找到用户: {user.email} (ID: {user.id})")
        
        # 测试关注列表统计
        stock_service = StockDataService(db.session)
        watchlist_data = stock_service.get_user_watchlist(user.id)
        
        print(f"\n📊 关注列表统计:")
        print(f"   关注股票数量: {watchlist_data['count']}")
        print(f"   最大关注数: {watchlist_data['max_count']}")
        print(f"   剩余额度: {watchlist_data['remaining_slots']}")
        
        # 测试分析报告统计
        analysis_service = AnalysisService(db.session)
        user_reports = analysis_service.get_user_reports(user.id, limit=100)
        reports_count = len(user_reports)
        
        print(f"\n📄 分析报告统计:")
        print(f"   报告数量: {reports_count}")
        
        # 显示关注列表详情
        print(f"\n📋 关注列表详情:")
        for item in watchlist_data['watchlist']:
            stock = item['stock']
            print(f"   - {stock['code']}: {stock['name']} (添加时间: {item['added_at']})")
        
        print(f"\n✅ 统计数据验证完成！")
        print(f"   仪表板应显示: 关注股票 {watchlist_data['count']}, 分析报告 {reports_count}")

if __name__ == "__main__":
    test_dashboard_stats()
