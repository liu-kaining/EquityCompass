"""
用户关注列表数据访问层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.repositories.base import SQLAlchemyRepository
from app.models.stock import UserWatchlist, Stock


class WatchlistRepository(SQLAlchemyRepository):
    """用户关注列表数据访问接口"""
    
    def __init__(self, session: Session):
        super().__init__(UserWatchlist, session)
    
    def get_user_watchlist(self, user_id: int) -> List[UserWatchlist]:
        """获取用户关注列表"""
        return self.get_all(user_id=user_id)
    
    def get_user_watchlist_with_stocks(self, user_id: int) -> List[dict]:
        """获取用户关注列表（包含股票详细信息）"""
        results = self.session.query(UserWatchlist, Stock).join(
            Stock, UserWatchlist.stock_id == Stock.id
        ).filter(UserWatchlist.user_id == user_id).all()
        
        watchlist = []
        for watchlist_item, stock in results:
            watchlist.append({
                'id': watchlist_item.id,
                'user_id': watchlist_item.user_id,
                'stock_id': watchlist_item.stock_id,
                'created_at': watchlist_item.added_at,
                'stock': {
                    'id': stock.id,
                    'code': stock.code,
                    'name': stock.name,
                    'market': stock.market,
                    'exchange': stock.exchange,
                    'industry': stock.industry
                }
            })
        return watchlist
    
    def add_to_watchlist(self, user_id: int, stock_id: int) -> Optional[UserWatchlist]:
        """添加股票到关注列表"""
        # 检查是否已经关注
        existing = self.session.query(UserWatchlist).filter(
            and_(UserWatchlist.user_id == user_id, UserWatchlist.stock_id == stock_id)
        ).first()
        
        if existing:
            return existing
        
        # 检查关注数量限制（最多20支）
        count = self.count(user_id=user_id)
        if count >= 20:
            raise ValueError("关注列表已满，最多只能关注20支股票")
        
        # 添加到关注列表
        watchlist_data = {
            'user_id': user_id,
            'stock_id': stock_id
        }
        return self.create(watchlist_data)
    
    def remove_from_watchlist(self, user_id: int, stock_id: int) -> bool:
        """从关注列表移除股票"""
        watchlist_item = self.session.query(UserWatchlist).filter(
            and_(UserWatchlist.user_id == user_id, UserWatchlist.stock_id == stock_id)
        ).first()
        
        if watchlist_item:
            self.session.delete(watchlist_item)
            self.session.commit()
            return True
        return False
    
    def is_watching(self, user_id: int, stock_id: int) -> bool:
        """检查用户是否已关注某股票"""
        return self.session.query(UserWatchlist).filter(
            and_(UserWatchlist.user_id == user_id, UserWatchlist.stock_id == stock_id)
        ).first() is not None
    
    def get_watchlist_count(self, user_id: int) -> int:
        """获取用户关注股票数量"""
        return self.count(user_id=user_id)
    
    def get_user_stock_codes(self, user_id: int) -> List[str]:
        """获取用户关注的股票代码列表"""
        results = self.session.query(Stock.code).join(
            UserWatchlist, UserWatchlist.stock_id == Stock.id
        ).filter(UserWatchlist.user_id == user_id).all()
        
        return [result[0] for result in results]
    
    def clear_watchlist(self, user_id: int) -> int:
        """清空用户关注列表"""
        deleted_count = self.session.query(UserWatchlist).filter(
            UserWatchlist.user_id == user_id
        ).delete()
        self.session.commit()
        return deleted_count
