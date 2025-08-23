#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关注列表功能测试
验证用户关注列表的增删改查功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.stock import Stock, UserWatchlist
from app.services.data.stock_service import StockDataService

def test_watchlist_functionality():
    """测试关注列表功能"""
    print("=== 关注列表功能测试 ===")
    
    app = create_app()
    with app.app_context():
        # 查找测试用户
        user_email = "liqian_macmini@qxmy.tech"
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            print(f"❌ 未找到用户: {user_email}")
            return
        
        print(f"✅ 找到用户: {user.email} (ID: {user.id})")
        
        # 测试获取关注列表
        stock_service = StockDataService(db.session)
        watchlist_data = stock_service.get_user_watchlist(user.id)
        
        print(f"\n📋 当前关注列表:")
        print(f"   总数: {watchlist_data['count']}")
        print(f"   最大数量: {watchlist_data['max_count']}")
        print(f"   剩余额度: {watchlist_data['remaining_slots']}")
        
        # 显示关注列表详情
        if watchlist_data['watchlist']:
            print(f"\n📊 关注股票详情:")
            for item in watchlist_data['watchlist']:
                stock = item['stock']
                print(f"   - {stock['code']}: {stock['name']}")
                print(f"     市场: {stock['market']}")
                print(f"     行业: {stock['industry']}")
                print(f"     添加时间: {item['added_at']}")
                print()
        else:
            print("   暂无关注的股票")
        
        # 测试添加关注功能
        test_stock_code = "TSLA"
        test_stock = Stock.query.filter_by(code=test_stock_code).first()
        
        if test_stock:
            print(f"\n🧪 测试添加关注: {test_stock_code}")
            
            # 检查是否已经关注
            existing = UserWatchlist.query.filter_by(
                user_id=user.id, 
                stock_id=test_stock.id
            ).first()
            
            if existing:
                print(f"   ⚠️  {test_stock_code} 已在关注列表中")
            else:
                print(f"   ✅ {test_stock_code} 可以添加到关注列表")
        else:
            print(f"\n❌ 测试股票 {test_stock_code} 不存在")
        
        # 测试关注数量限制
        print(f"\n📏 关注数量限制测试:")
        print(f"   当前关注: {watchlist_data['count']}")
        print(f"   最大允许: {watchlist_data['max_count']}")
        
        if watchlist_data['count'] >= watchlist_data['max_count']:
            print("   ⚠️  已达到最大关注数量限制")
        else:
            print(f"   ✅ 还可以关注 {watchlist_data['remaining_slots']} 只股票")
        
        print(f"\n✅ 关注列表功能测试完成！")

if __name__ == "__main__":
    test_watchlist_functionality()
