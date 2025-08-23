#!/usr/bin/env python3
"""
测试关注列表功能
"""
from app import create_app, db
from app.models.user import User
from app.models.stock import Stock, UserWatchlist
from app.services.data.stock_service import StockDataService

def test_watchlist_functionality():
    app = create_app()
    with app.app_context():
        print("=== 测试关注列表功能 ===")
        
        # 获取用户
        user = User.query.first()
        if not user:
            print("❌ 没有找到用户")
            return
        
        print(f"✅ 找到用户: {user.email}")
        
        # 获取股票服务
        service = StockDataService(db.session)
        
        # 测试获取关注列表
        print("\n1. 测试获取关注列表")
        watchlist_data = service.get_user_watchlist(user.id)
        print(f"   关注列表数量: {watchlist_data['count']}")
        print(f"   最大关注数: {watchlist_data['max_count']}")
        print(f"   剩余额度: {watchlist_data['remaining_slots']}")
        
        # 显示当前关注的股票
        print("\n2. 当前关注的股票:")
        for item in watchlist_data['watchlist']:
            print(f"   - {item['stock']['code']}: {item['stock']['name']} (添加时间: {item['added_at']})")
        
        # 测试添加关注
        print("\n3. 测试添加关注")
        test_stock = Stock.query.filter(Stock.code == 'MSFT').first()
        if test_stock:
            print(f"   测试股票: {test_stock.code} - {test_stock.name}")
            
            # 检查是否已经关注
            is_watching = any(item['stock']['code'] == test_stock.code for item in watchlist_data['watchlist'])
            if is_watching:
                print(f"   ⚠️  {test_stock.code} 已经在关注列表中")
            else:
                print(f"   ➕ 添加 {test_stock.code} 到关注列表")
                result = service.add_to_watchlist(user.id, test_stock.code)
                print(f"   结果: {result}")
        
        # 重新获取关注列表
        print("\n4. 重新获取关注列表")
        updated_watchlist = service.get_user_watchlist(user.id)
        print(f"   更新后关注列表数量: {updated_watchlist['count']}")
        
        # 显示更新后的关注列表
        print("\n5. 更新后的关注列表:")
        for item in updated_watchlist['watchlist']:
            print(f"   - {item['stock']['code']}: {item['stock']['name']} (添加时间: {item['added_at']})")

if __name__ == "__main__":
    test_watchlist_functionality()
