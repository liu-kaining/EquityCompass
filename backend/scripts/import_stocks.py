#!/usr/bin/env python3
"""
股票数据导入脚本
从JSON文件导入股票数据到数据库
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.stock import Stock


def import_stocks():
    """导入股票数据"""
    app = create_app()
    
    with app.app_context():
        # 读取股票数据文件
        stocks_file = os.path.join(app.root_path, '..', 'data', 'stocks_comprehensive.json')
        
        if not os.path.exists(stocks_file):
            print(f"错误：找不到股票数据文件 {stocks_file}")
            return
        
        try:
            with open(stocks_file, 'r', encoding='utf-8') as f:
                stocks_data = json.load(f)
        except Exception as e:
            print(f"错误：读取股票数据文件失败 - {e}")
            return
        
        print(f"开始导入 {len(stocks_data)} 只股票...")
        
        # 清空现有股票数据
        Stock.query.delete()
        db.session.commit()
        print("已清空现有股票数据")
        
        # 导入新数据
        imported_count = 0
        for stock_info in stocks_data:
            try:
                # 创建股票对象
                stock = Stock(
                    code=stock_info['code'],
                    name=stock_info['name'],
                    market=stock_info['market'],
                    industry=stock_info.get('industry', ''),
                    exchange=stock_info.get('exchange', ''),
                    stock_type='BUILT_IN',  # 设置为内置股票类型
                    market_cap=0,  # 默认市值
                    created_by_user_id=1,  # 系统用户ID
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.session.add(stock)
                imported_count += 1
                
                if imported_count % 50 == 0:
                    print(f"已导入 {imported_count} 只股票...")
                    
            except Exception as e:
                print(f"错误：导入股票 {stock_info.get('code', 'Unknown')} 失败 - {e}")
                continue
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"成功导入 {imported_count} 只股票到数据库")
        except Exception as e:
            print(f"错误：提交数据库更改失败 - {e}")
            db.session.rollback()


if __name__ == '__main__':
    import_stocks()
