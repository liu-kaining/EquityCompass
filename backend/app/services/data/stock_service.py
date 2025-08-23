"""
股票数据服务
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories.stock_repository import StockRepository
from app.repositories.watchlist_repository import WatchlistRepository
from app.utils.timezone import format_local_time


class StockDataService:
    """股票数据服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.stock_repo = StockRepository(session)
        self.watchlist_repo = WatchlistRepository(session)
    
    def get_stock_pools(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取股票池（美股TOP100 + 港股TOP100）"""
        us_stocks = self.stock_repo.get_us_top100()
        hk_stocks = self.stock_repo.get_hk_top100()
        
        return {
            'us_stocks': [self._format_stock(stock) for stock in us_stocks],
            'hk_stocks': [self._format_stock(stock) for stock in hk_stocks],
            'total_count': len(us_stocks) + len(hk_stocks)
        }
    
    def search_stocks(self, keyword: str, market: str = None, user_id: int = None) -> List[Dict[str, Any]]:
        """搜索股票"""
        stocks = self.stock_repo.search_stocks(keyword, market)
        
        # 如果提供了用户ID，标记用户是否已关注
        user_watchlist = set()
        if user_id:
            user_stock_codes = self.watchlist_repo.get_user_stock_codes(user_id)
            user_watchlist = set(user_stock_codes)
        
        results = []
        for stock in stocks:
            stock_data = self._format_stock(stock)
            if user_id:
                stock_data['is_watching'] = stock.code in user_watchlist
            results.append(stock_data)
        
        return results
    
    def get_stock_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """根据代码获取股票"""
        stock = self.stock_repo.get_by_code(code)
        return self._format_stock(stock) if stock else None
    
    def add_custom_stock(self, code: str, name: str, market: str, user_id: int, **kwargs) -> Dict[str, Any]:
        """添加自定义股票"""
        # 检查股票是否已存在
        if self.stock_repo.exists_by_code(code):
            raise ValueError(f"股票代码 {code} 已存在")
        
        # 验证市场类型
        if market not in ['US', 'HK']:
            raise ValueError("市场类型必须是 US 或 HK")
        
        # 创建股票
        stock_data = {
            'code': code.upper(),
            'name': name,
            'market': market,
            'stock_type': 'USER_ADDED',
            'created_by': user_id,
            **kwargs
        }
        
        stock = self.stock_repo.create_stock(**stock_data)
        return self._format_stock(stock)
    
    def get_user_watchlist(self, user_id: int) -> Dict[str, Any]:
        """获取用户关注列表"""
        watchlist = self.watchlist_repo.get_user_watchlist_with_stocks(user_id)
        
        return {
            'watchlist': watchlist,
            'count': len(watchlist),
            'max_count': 20,
            'remaining_slots': 20 - len(watchlist)
        }
    
    def add_to_watchlist(self, user_id: int, stock_code: str) -> Dict[str, Any]:
        """添加股票到关注列表"""
        # 获取股票
        stock = self.stock_repo.get_by_code(stock_code)
        if not stock:
            raise ValueError(f"股票代码 {stock_code} 不存在")
        
        # 添加到关注列表
        try:
            watchlist_item = self.watchlist_repo.add_to_watchlist(user_id, stock.id)
            return {
                'success': True,
                'message': f'已添加 {stock.code} 到关注列表',
                'watchlist_item': {
                    'id': watchlist_item.id,
                    'stock': self._format_stock(stock),
                    'added_at': format_local_time(watchlist_item.added_at) if watchlist_item.added_at else None
                }
            }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def remove_from_watchlist(self, user_id: int, stock_code: str) -> Dict[str, Any]:
        """从关注列表移除股票"""
        stock = self.stock_repo.get_by_code(stock_code)
        if not stock:
            raise ValueError(f"股票代码 {stock_code} 不存在")
        
        success = self.watchlist_repo.remove_from_watchlist(user_id, stock.id)
        
        return {
            'success': success,
            'message': f'已从关注列表移除 {stock.code}' if success else '移除失败'
        }
    
    def clear_watchlist(self, user_id: int) -> Dict[str, Any]:
        """一键清空关注列表"""
        try:
            deleted_count = self.watchlist_repo.clear_watchlist(user_id)
            return {
                'success': True,
                'message': f'已清空关注列表，共移除 {deleted_count} 支股票',
                'deleted_count': deleted_count
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'清空失败: {str(e)}'
            }
    
    def get_watchlist_stocks_for_analysis(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户关注的股票列表（用于分析）"""
        watchlist = self.watchlist_repo.get_user_watchlist_with_stocks(user_id)
        
        stocks = []
        for item in watchlist:
            stocks.append({
                'code': item['stock']['code'],
                'name': item['stock']['name'],
                'market': item['stock']['market'],
                'exchange': item['stock']['exchange'],
                'industry': item['stock']['industry']
            })
        
        return stocks
    
    def _format_stock(self, stock) -> Dict[str, Any]:
        """格式化股票数据"""
        if not stock:
            return None
        
        return {
            'id': stock.id,
            'code': stock.code,
            'name': stock.name,
            'market': stock.market,
            'exchange': stock.exchange,
            'industry': stock.industry,
            'stock_type': stock.stock_type,
            'market_cap': stock.market_cap,
            'created_at': stock.created_at.isoformat() if stock.created_at else None
        }
