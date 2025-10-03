#!/usr/bin/env python3
"""
创建金币系统数据库表
用于在现有数据库中添加金币相关表

使用方法：
python scripts/create_coin_tables.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models.coin import UserCoin, CoinTransaction, CoinPackage, CoinOrder, DailyBonus


def create_coin_tables():
    """创建金币系统相关表"""
    app = create_app()
    
    with app.app_context():
        print("开始创建金币系统数据库表...")
        
        try:
            # 创建所有金币相关表
            db.create_all()
            print("✅ 金币系统数据库表创建成功")
            
            # 验证表是否创建成功
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            coin_tables = ['user_coins', 'coin_transactions', 'coin_packages', 'coin_orders', 'daily_bonuses']
            created_tables = [table for table in coin_tables if table in tables]
            
            print(f"已创建的表: {created_tables}")
            
            if len(created_tables) == len(coin_tables):
                print("✅ 所有金币系统表都已成功创建")
            else:
                missing_tables = set(coin_tables) - set(created_tables)
                print(f"❌ 缺少表: {missing_tables}")
                
        except Exception as e:
            print(f"❌ 创建表时发生错误: {str(e)}")
            raise


if __name__ == '__main__':
    create_coin_tables()