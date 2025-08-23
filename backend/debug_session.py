#!/usr/bin/env python3
"""
调试用户session和关注列表
"""
from app import create_app, db
from app.models.user import User
from app.models.stock import Stock, UserWatchlist
from app.services.data.stock_service import StockDataService

def debug_session_and_watchlist():
    app = create_app()
    with app.app_context():
        print("=== 调试用户Session和关注列表 ===")
        
        # 获取所有用户
        users = User.query.all()
        print(f"总用户数: {len(users)}")
        
        for user in users:
            print(f"\n用户: {user.email} (ID: {user.id})")
            
            # 检查该用户的关注列表
            watchlist_items = UserWatchlist.query.filter_by(user_id=user.id).all()
            print(f"  关注列表数量: {len(watchlist_items)}")
            
            if watchlist_items:
                print("  关注的股票:")
                for item in watchlist_items:
                    stock = Stock.query.get(item.stock_id)
                    if stock:
                        print(f"    - {stock.code}: {stock.name} (添加时间: {item.added_at})")
                    else:
                        print(f"    - 股票ID {item.stock_id} 不存在")
            else:
                print("  没有关注任何股票")
        
        # 测试特定用户的关注列表
        print("\n=== 测试特定用户的关注列表 ===")
        test_user = User.query.filter_by(email='liqian_macmini@qxmy.tech').first()
        if test_user:
            print(f"测试用户: {test_user.email} (ID: {test_user.id})")
            
            service = StockDataService(db.session)
            watchlist_data = service.get_user_watchlist(test_user.id)
            
            print(f"服务层返回的关注列表数量: {watchlist_data['count']}")
            print("服务层返回的关注列表:")
            for item in watchlist_data['watchlist']:
                print(f"  - {item['stock']['code']}: {item['stock']['name']} (添加时间: {item['added_at']})")
        else:
            print("❌ 没有找到测试用户 liqian_macmini@qxmy.tech")

if __name__ == "__main__":
    debug_session_and_watchlist()
