#!/usr/bin/env python3
"""
测试股票详情页面
"""
from app import create_app, db
from app.models.stock import Stock
from app.services.data.stock_service import StockDataService

def test_stock_detail():
    app = create_app()
    with app.app_context():
        print("=== 测试股票详情页面 ===")
        
        # 获取股票服务
        service = StockDataService(db.session)
        
        # 测试获取股票详情
        test_stocks = ['AAPL', 'MSFT', 'GOOGL']
        
        for stock_code in test_stocks:
            print(f"\n测试股票: {stock_code}")
            stock = service.get_stock_by_code(stock_code)
            
            if stock:
                print(f"  ✅ 找到股票: {stock['code']} - {stock['name']}")
                print(f"     市场: {stock['market']}")
                print(f"     行业: {stock['industry']}")
                print(f"     类型: {stock['stock_type']}")
            else:
                print(f"  ❌ 未找到股票: {stock_code}")
        
        # 测试获取股票池
        print("\n=== 测试股票池 ===")
        stock_pools = service.get_stock_pools()
        print(f"美股数量: {len(stock_pools['us_stocks'])}")
        print(f"港股数量: {len(stock_pools['hk_stocks'])}")
        print(f"总数: {stock_pools['total_count']}")

if __name__ == "__main__":
    test_stock_detail()
