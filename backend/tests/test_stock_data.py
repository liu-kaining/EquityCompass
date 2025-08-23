#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据功能测试
验证股票数据的增删改查功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.stock import Stock
from app.services.data.stock_service import StockDataService

def test_stock_data():
    """测试股票数据功能"""
    print("=== 股票数据功能测试 ===")
    
    app = create_app()
    with app.app_context():
        stock_service = StockDataService(db.session)
        
        # 测试获取股票池
        print("📊 测试获取股票池...")
        stock_pools = stock_service.get_stock_pools()
        
        print(f"   美股数量: {len(stock_pools['us_stocks'])}")
        print(f"   港股数量: {len(stock_pools['hk_stocks'])}")
        print(f"   总数: {stock_pools['total_count']}")
        
        # 显示前5只美股
        print(f"\n📋 美股样本:")
        for i, stock in enumerate(stock_pools['us_stocks'][:5]):
            print(f"   {i+1}. {stock['code']}: {stock['name']}")
            print(f"      市场: {stock['market']}")
            print(f"      行业: {stock['industry']}")
        
        # 测试搜索功能
        print(f"\n🔍 测试搜索功能...")
        search_results = stock_service.search_stocks("AAPL")
        print(f"   搜索 'AAPL' 结果: {len(search_results)} 只股票")
        
        if search_results:
            stock = search_results[0]
            print(f"   找到: {stock['code']} - {stock['name']}")
        
        # 测试市场筛选
        print(f"\n🏢 测试市场筛选...")
        us_stocks = stock_pools['us_stocks']
        print(f"   美股数量: {len(us_stocks)}")
        
        # 测试获取单只股票详情
        print(f"\n📈 测试股票详情...")
        test_stock_code = "AAPL"
        stock_detail = stock_service.get_stock_by_code(test_stock_code)
        
        if stock_detail:
            print(f"   ✅ 找到股票: {stock_detail['code']}")
            print(f"      名称: {stock_detail['name']}")
            print(f"      市场: {stock_detail['market']}")
            print(f"      行业: {stock_detail['industry']}")
        else:
            print(f"   ❌ 未找到股票: {test_stock_code}")
        
        # 测试数据库统计
        print(f"\n📊 数据库统计:")
        total_stocks = Stock.query.count()
        us_stocks_count = Stock.query.filter_by(market="US").count()
        print(f"   总股票数: {total_stocks}")
        print(f"   美股数量: {us_stocks_count}")
        
        # 测试热门股票
        print(f"\n🔥 热门股票样本:")
        popular_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
        for code in popular_stocks:
            stock = stock_service.get_stock_by_code(code)
            if stock:
                print(f"   - {stock['code']}: {stock['name']}")
        
        print(f"\n✅ 股票数据功能测试完成！")

if __name__ == "__main__":
    test_stock_data()
