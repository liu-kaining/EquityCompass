#!/usr/bin/env python3
"""
股票数据导入脚本
支持从CSV或JSON文件导入股票数据
"""
import os
import sys
import csv
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.stock import Stock

def import_from_csv(file_path: str):
    """从CSV文件导入股票数据"""
    print(f"📁 从CSV文件导入: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        stocks = []
        
        for row in reader:
            # 字段映射和兼容性处理
            stock_data = {}
            
            # 必需字段
            required_fields = ['code', 'name', 'market']
            for field in required_fields:
                if field not in row or not row[field].strip():
                    print(f"⚠️  跳过缺少必需字段 {field} 的行: {row}")
                    continue
            
            stock_data['code'] = row['code'].strip().upper()
            stock_data['name'] = row['name'].strip()
            stock_data['market'] = row['market'].strip()
            
            # 可选字段
            if 'industry' in row and row['industry'].strip():
                stock_data['industry'] = row['industry'].strip()
            
            if 'exchange' in row and row['exchange'].strip():
                stock_data['exchange'] = row['exchange'].strip()
            
            # 股票类型判断
            if 'is_builtin' in row:
                stock_data['stock_type'] = 'BUILT_IN' if row['is_builtin'].strip() == '1' else 'USER_ADDED'
            elif 'stock_type' in row:
                stock_data['stock_type'] = row['stock_type'].strip()
            else:
                stock_data['stock_type'] = 'BUILT_IN'  # 默认内置
            
            # 市值处理
            if 'market_cap' in row and row['market_cap'].strip():
                try:
                    # 支持不同格式的市值（如 "3.0T", "800B", "250M" 等）
                    market_cap_str = row['market_cap'].strip().upper()
                    if market_cap_str.endswith('T'):
                        market_cap = int(float(market_cap_str[:-1]) * 1e12)
                    elif market_cap_str.endswith('B'):
                        market_cap = int(float(market_cap_str[:-1]) * 1e9)
                    elif market_cap_str.endswith('M'):
                        market_cap = int(float(market_cap_str[:-1]) * 1e6)
                    else:
                        market_cap = int(float(market_cap_str))
                    stock_data['market_cap'] = market_cap
                except (ValueError, TypeError) as e:
                    print(f"⚠️  市值格式错误 {row['market_cap']}: {e}")
            
            # 创建股票对象
            try:
                stock = Stock(**stock_data)
                stocks.append(stock)
            except Exception as e:
                print(f"❌ 创建股票对象失败 {stock_data}: {e}")
        
        return stocks

def import_from_json(file_path: str):
    """从JSON文件导入股票数据"""
    print(f"📁 从JSON文件导入: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        stocks = []
        
        for item in data:
            # 字段映射和兼容性处理
            stock_data = {}
            
            # 必需字段检查
            required_fields = ['code', 'name', 'market']
            for field in required_fields:
                if field not in item or not str(item[field]).strip():
                    print(f"⚠️  跳过缺少必需字段 {field} 的项目: {item}")
                    continue
            
            stock_data['code'] = str(item['code']).strip().upper()
            stock_data['name'] = str(item['name']).strip()
            stock_data['market'] = str(item['market']).strip()
            
            # 可选字段
            if 'industry' in item and item['industry']:
                stock_data['industry'] = str(item['industry']).strip()
            
            if 'exchange' in item and item['exchange']:
                stock_data['exchange'] = str(item['exchange']).strip()
            
            # 股票类型判断
            if 'is_builtin' in item:
                stock_data['stock_type'] = 'BUILT_IN' if item['is_builtin'] else 'USER_ADDED'
            elif 'stock_type' in item:
                stock_data['stock_type'] = str(item['stock_type']).strip()
            else:
                stock_data['stock_type'] = 'BUILT_IN'  # 默认内置
            
            # 市值处理
            if 'market_cap' in item and item['market_cap']:
                try:
                    market_cap = item['market_cap']
                    if isinstance(market_cap, str):
                        # 支持不同格式的市值（如 "3.0T", "800B", "250M" 等）
                        market_cap_str = market_cap.strip().upper()
                        if market_cap_str.endswith('T'):
                            market_cap = int(float(market_cap_str[:-1]) * 1e12)
                        elif market_cap_str.endswith('B'):
                            market_cap = int(float(market_cap_str[:-1]) * 1e9)
                        elif market_cap_str.endswith('M'):
                            market_cap = int(float(market_cap_str[:-1]) * 1e6)
                        else:
                            market_cap = int(float(market_cap_str))
                    else:
                        market_cap = int(market_cap)
                    stock_data['market_cap'] = market_cap
                except (ValueError, TypeError) as e:
                    print(f"⚠️  市值格式错误 {item['market_cap']}: {e}")
            
            # 创建股票对象
            try:
                stock = Stock(**stock_data)
                stocks.append(stock)
            except Exception as e:
                print(f"❌ 创建股票对象失败 {stock_data}: {e}")
        
        return stocks

def import_stocks(file_path: str):
    """导入股票数据"""
    app = create_app()
    
    with app.app_context():
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return
        
        # 根据文件扩展名选择导入方法
        if file_path.endswith('.csv'):
            stocks = import_from_csv(file_path)
        elif file_path.endswith('.json'):
            stocks = import_from_json(file_path)
        else:
            print("❌ 不支持的文件格式，请使用CSV或JSON文件")
            return
        
        print(f"📊 准备导入 {len(stocks)} 只股票...")
        
        # 检查重复股票
        existing_codes = set()
        new_stocks = []
        
        for stock in stocks:
            existing = Stock.query.filter_by(code=stock.code).first()
            if existing:
                existing_codes.add(stock.code)
                print(f"⚠️  股票已存在: {stock.code} - {stock.name}")
            else:
                new_stocks.append(stock)
        
        if existing_codes:
            print(f"⚠️  跳过 {len(existing_codes)} 只已存在的股票")
        
        if new_stocks:
            # 批量插入新股票
            db.session.add_all(new_stocks)
            db.session.commit()
            print(f"✅ 成功导入 {len(new_stocks)} 只新股票")
            
            # 显示导入的股票
            print("\n📋 导入的股票列表:")
            for stock in new_stocks:
                print(f"  - {stock.code}: {stock.name} ({stock.market})")
        else:
            print("ℹ️  没有新的股票需要导入")

def main():
    """主函数"""
    print("🚀 股票数据导入工具")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("用法: python import_stocks.py <文件路径>")
        print("示例:")
        print("  python import_stocks.py data/stocks_sample.csv")
        print("  python import_stocks.py data/stocks_sample.json")
        return
    
    file_path = sys.argv[1]
    import_stocks(file_path)

if __name__ == "__main__":
    main()
