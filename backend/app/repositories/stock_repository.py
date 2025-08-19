"""
股票数据访问层
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import SQLAlchemyRepository
from app.models.stock import Stock


class StockRepository(SQLAlchemyRepository):
    """股票数据访问接口"""
    
    def __init__(self, session: Session):
        super().__init__(Stock, session)
    
    def get_by_code(self, code: str) -> Optional[Stock]:
        """根据股票代码获取股票"""
        return self.session.query(Stock).filter(Stock.code == code).first()
    
    def search_stocks(self, keyword: str, market: str = None) -> List[Stock]:
        """搜索股票（按代码或名称）"""
        query = self.session.query(Stock).filter(
            (Stock.code.ilike(f'%{keyword}%')) | 
            (Stock.name.ilike(f'%{keyword}%'))
        )
        
        if market:
            query = query.filter(Stock.market == market)
        
        return query.limit(50).all()  # 限制返回数量
    
    def get_by_market(self, market: str) -> List[Stock]:
        """根据市场获取股票"""
        return self.get_all(market=market)
    
    def get_builtin_stocks(self) -> List[Stock]:
        """获取内置股票池"""
        return self.get_all(stock_type='BUILT_IN')
    
    def get_us_top100(self) -> List[Stock]:
        """获取美股TOP100"""
        return self.session.query(Stock).filter(
            Stock.market == 'US',
            Stock.stock_type == 'BUILT_IN'
        ).order_by(Stock.market_cap.desc()).limit(100).all()
    
    def get_hk_top100(self) -> List[Stock]:
        """获取港股TOP100"""
        return self.session.query(Stock).filter(
            Stock.market == 'HK',
            Stock.stock_type == 'BUILT_IN'
        ).order_by(Stock.market_cap.desc()).limit(100).all()
    
    def create_stock(self, code: str, name: str, market: str, 
                    stock_type: str = 'USER_ADDED', **kwargs) -> Stock:
        """创建股票"""
        stock_data = {
            'code': code.upper(),
            'name': name,
            'market': market,
            'stock_type': stock_type,
            **kwargs
        }
        return self.create(stock_data)
    
    def bulk_create_stocks(self, stocks_data: List[dict]) -> List[Stock]:
        """批量创建股票"""
        stocks = []
        for data in stocks_data:
            stock = Stock(**data)
            self.session.add(stock)
            stocks.append(stock)
        
        self.session.commit()
        return stocks
    
    def exists_by_code(self, code: str) -> bool:
        """检查股票代码是否存在"""
        return self.session.query(Stock).filter(Stock.code == code).first() is not None
