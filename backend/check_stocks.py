#!/usr/bin/env python3
"""
检查数据库中的股票数据
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.stock import Stock

def check_stocks():
    """检查股票数据"""
    print("📊 检查数据库中的股票数据...")
    
    app = create_app()
    
    with app.app_context():
        # 统计总数
        total_stocks = Stock.query.count()
        print(f"\n📈 股票总数: {total_stocks}")
        
        # 按市场统计
        us_stocks = Stock.query.filter_by(market='US').count()
        hk_stocks = Stock.query.filter_by(market='HK').count()
        print(f"🇺🇸 美股: {us_stocks} 只")
        print(f"🇭🇰 港股: {hk_stocks} 只")
        
        # 按类型统计
        builtin_stocks = Stock.query.filter_by(stock_type='BUILT_IN').count()
        custom_stocks = Stock.query.filter_by(stock_type='USER_ADDED').count()
        print(f"🏢 内置股票: {builtin_stocks} 只")
        print(f"👤 用户自定义: {custom_stocks} 只")
        
        # 按行业统计（前10个）
        print(f"\n🏭 行业分布 (前10个):")
        from sqlalchemy import func
        industry_stats = db.session.query(
            Stock.industry, 
            func.count(Stock.id).label('count')
        ).filter(
            Stock.industry.isnot(None)
        ).group_by(
            Stock.industry
        ).order_by(
            func.count(Stock.id).desc()
        ).limit(10).all()
        
        for industry, count in industry_stats:
            print(f"  - {industry}: {count} 只")
        
        # 显示一些示例股票
        print(f"\n📋 示例股票 (前10只):")
        sample_stocks = Stock.query.limit(10).all()
        for stock in sample_stocks:
            print(f"  - {stock.code}: {stock.name} ({stock.market}) - {stock.industry}")
        
        # 检查是否有重复
        print(f"\n🔍 检查重复股票代码...")
        from sqlalchemy import func
        duplicates = db.session.query(
            Stock.code, 
            func.count(Stock.id).label('count')
        ).group_by(
            Stock.code
        ).having(
            func.count(Stock.id) > 1
        ).all()
        
        if duplicates:
            print(f"⚠️  发现重复股票代码:")
            for code, count in duplicates:
                print(f"  - {code}: {count} 次")
        else:
            print(f"✅ 没有重复股票代码")

if __name__ == "__main__":
    check_stocks()
