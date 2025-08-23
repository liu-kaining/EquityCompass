#!/usr/bin/env python3
"""
检查关注列表数据
"""
from app import create_app, db
from app.models.user import User
from app.models.stock import Stock, UserWatchlist

def main():
    app = create_app()
    with app.app_context():
        print("=== 数据库状态检查 ===")
        print(f"用户数量: {User.query.count()}")
        print(f"股票数量: {Stock.query.count()}")
        print(f"关注列表数量: {UserWatchlist.query.count()}")
        
        print("\n=== 关注列表详情 ===")
        watchlist_items = UserWatchlist.query.all()
        if watchlist_items:
            for item in watchlist_items:
                stock = Stock.query.get(item.stock_id)
                user = User.query.get(item.user_id)
                print(f"用户: {user.email if user else 'Unknown'}, 股票: {stock.code if stock else 'Unknown'}, 添加时间: {item.added_at}")
        else:
            print("没有关注列表数据")
        
        print("\n=== 股票样本 ===")
        stocks = Stock.query.limit(5).all()
        for stock in stocks:
            print(f"股票代码: {stock.code}, 名称: {stock.name}, 市场: {stock.market}")

if __name__ == "__main__":
    main()
