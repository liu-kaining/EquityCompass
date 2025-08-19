"""
数据库服务 - 初始化和数据填充
"""
import os
from typing import List, Dict
from sqlalchemy.orm import Session
from app import db
from app.repositories.stock_repository import StockRepository


class DatabaseService:
    """数据库初始化和管理服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.stock_repo = StockRepository(session)
    
    def initialize_database(self):
        """初始化数据库"""
        try:
            # 确保数据库文件目录存在
            from flask import current_app
            db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
            print(f"📊 数据库URI: {db_uri}")
            
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri[10:]  # 移除 'sqlite:///' 前缀
                db_dir = os.path.dirname(db_path) if '/' in db_path else '.'
                
                if db_dir and db_dir != '.':
                    os.makedirs(db_dir, exist_ok=True)
                    print(f"📁 创建数据库目录: {db_dir}")
            
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功")
            
            # 填充基础数据
            self.populate_stock_pools()
            print("✅ 基础数据填充完成")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            raise
    
    def populate_stock_pools(self):
        """填充股票池数据"""
        # 检查是否已有数据
        if self.stock_repo.count() > 0:
            print("📊 股票池数据已存在，跳过填充")
            return
        
        # 美股TOP100数据
        us_stocks = self._get_us_top100_data()
        # 港股TOP100数据  
        hk_stocks = self._get_hk_top100_data()
        
        all_stocks = us_stocks + hk_stocks
        
        # 批量创建股票
        self.stock_repo.bulk_create_stocks(all_stocks)
        
        print(f"📈 已添加 {len(us_stocks)} 支美股")
        print(f"📈 已添加 {len(hk_stocks)} 支港股")
        print(f"📈 股票池总计: {len(all_stocks)} 支股票")
    
    def _get_us_top100_data(self) -> List[Dict]:
        """获取美股TOP100数据（示例数据）"""
        # 这里是示例数据，实际应该从金融数据API获取
        us_stocks = [
            {
                'code': 'AAPL',
                'name': '苹果公司',
                'market': 'US',
                'exchange': 'NASDAQ',
                'industry': '消费电子',
                'stock_type': 'BUILT_IN',
                'market_cap': 3000000000000  # 3万亿美元
            },
            {
                'code': 'MSFT',
                'name': '微软公司',
                'market': 'US',
                'exchange': 'NASDAQ',
                'industry': '软件服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 2800000000000
            },
            {
                'code': 'GOOGL',
                'name': '谷歌',
                'market': 'US',
                'exchange': 'NASDAQ',
                'industry': '互联网服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 1700000000000
            },
            {
                'code': 'AMZN',
                'name': '亚马逊',
                'market': 'US',
                'exchange': 'NASDAQ',
                'industry': '电子商务',
                'stock_type': 'BUILT_IN',
                'market_cap': 1500000000000
            },
            {
                'code': 'TSLA',
                'name': '特斯拉',
                'market': 'US',
                'exchange': 'NASDAQ',
                'industry': '电动汽车',
                'stock_type': 'BUILT_IN',
                'market_cap': 800000000000
            },
            {
                'code': 'META',
                'name': 'Meta平台',
                'market': 'US',
                'exchange': 'NASDAQ',
                'industry': '社交媒体',
                'stock_type': 'BUILT_IN',
                'market_cap': 750000000000
            },
            {
                'code': 'NVDA',
                'name': '英伟达',
                'market': 'US',
                'exchange': 'NASDAQ',
                'industry': '半导体',
                'stock_type': 'BUILT_IN',
                'market_cap': 1200000000000
            },
            {
                'code': 'NFLX',
                'name': '奈飞',
                'market': 'US',
                'exchange': 'NASDAQ',
                'industry': '流媒体',
                'stock_type': 'BUILT_IN',
                'market_cap': 200000000000
            },
            {
                'code': 'JPM',
                'name': '摩根大通',
                'market': 'US',
                'exchange': 'NYSE',
                'industry': '金融服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 450000000000
            },
            {
                'code': 'V',
                'name': '维萨',
                'market': 'US',
                'exchange': 'NYSE',
                'industry': '支付服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 520000000000
            }
        ]
        
        # 为了演示，复制这10支股票到100支
        extended_stocks = []
        for i in range(10):
            for j, stock in enumerate(us_stocks):
                if len(extended_stocks) >= 100:
                    break
                
                # 为重复的股票添加序号
                if i > 0:
                    stock_copy = stock.copy()
                    stock_copy['code'] = f"{stock['code']}{i}"
                    stock_copy['name'] = f"{stock['name']} (系列{i})"
                    stock_copy['market_cap'] = stock['market_cap'] - (i * 10000000000)
                    extended_stocks.append(stock_copy)
                else:
                    extended_stocks.append(stock)
            
            if len(extended_stocks) >= 100:
                break
        
        return extended_stocks[:100]
    
    def _get_hk_top100_data(self) -> List[Dict]:
        """获取港股TOP100数据（示例数据）"""
        hk_stocks = [
            {
                'code': '00700',
                'name': '腾讯控股',
                'market': 'HK',
                'exchange': 'HKEX',
                'industry': '互联网服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 400000000000  # 港币
            },
            {
                'code': '09988',
                'name': '阿里巴巴-SW',
                'market': 'HK',
                'exchange': 'HKEX',
                'industry': '电子商务',
                'stock_type': 'BUILT_IN',
                'market_cap': 200000000000
            },
            {
                'code': '00941',
                'name': '中国移动',
                'market': 'HK',
                'exchange': 'HKEX',
                'industry': '电信服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 180000000000
            },
            {
                'code': '01299',
                'name': '友邦保险',
                'market': 'HK',
                'exchange': 'HKEX',
                'industry': '保险服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 150000000000
            },
            {
                'code': '03690',
                'name': '美团-W',
                'market': 'HK',
                'exchange': 'HKEX',
                'industry': '生活服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 120000000000
            },
            {
                'code': '00005',
                'name': '汇丰控股',
                'market': 'HK',
                'exchange': 'HKEX',
                'industry': '银行服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 140000000000
            },
            {
                'code': '01810',
                'name': '小米集团-W',
                'market': 'HK',
                'exchange': 'HKEX',
                'industry': '消费电子',
                'stock_type': 'BUILT_IN',
                'market_cap': 80000000000
            },
            {
                'code': '09618',
                'name': '京东集团-SW',
                'market': 'HK',
                'exchange': 'HKEX',
                'industry': '电子商务',
                'stock_type': 'BUILT_IN',
                'market_cap': 90000000000
            },
            {
                'code': '02318',
                'name': '中国平安',
                'market': 'HK',
                'exchange': 'HKEX',
                'industry': '保险服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 110000000000
            },
            {
                'code': '01398',
                'name': '工商银行',
                'market': 'HK',
                'exchange': 'HKEX',
                'industry': '银行服务',
                'stock_type': 'BUILT_IN',
                'market_cap': 130000000000
            }
        ]
        
        # 扩展到100支港股
        extended_stocks = []
        for i in range(10):
            for j, stock in enumerate(hk_stocks):
                if len(extended_stocks) >= 100:
                    break
                
                if i > 0:
                    stock_copy = stock.copy()
                    # 港股代码格式特殊处理
                    code_num = int(stock['code']) + (i * 10000)
                    stock_copy['code'] = f"{code_num:05d}"
                    stock_copy['name'] = f"{stock['name']} (系列{i})"
                    stock_copy['market_cap'] = stock['market_cap'] - (i * 1000000000)
                    extended_stocks.append(stock_copy)
                else:
                    extended_stocks.append(stock)
            
            if len(extended_stocks) >= 100:
                break
        
        return extended_stocks[:100]
    
    def reset_database(self):
        """重置数据库（危险操作）"""
        try:
            db.drop_all()
            print("🗑️  数据库已清空")
            self.initialize_database()
            print("🔄 数据库重置完成")
        except Exception as e:
            print(f"❌ 数据库重置失败: {e}")
            raise
