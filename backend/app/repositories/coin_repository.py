"""
金币系统仓库层
"""
from datetime import date, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from app.models.coin import UserCoin, CoinTransaction, CoinPackage, CoinOrder, DailyBonus
from app.repositories.base import SQLAlchemyRepository


class CoinRepository(SQLAlchemyRepository):
    """金币仓库"""
    
    def __init__(self, db_session: Session):
        # 使用UserCoin作为默认模型类
        super().__init__(UserCoin, db_session)
    
    # UserCoin 相关方法
    def get_user_coin(self, user_id: int) -> Optional[UserCoin]:
        """获取用户金币账户"""
        return self.session.query(UserCoin).filter(UserCoin.user_id == user_id).first()
    
    def create_user_coin(self, user_id: int, total_coins: int = 0, available_coins: int = 0, frozen_coins: int = 0) -> UserCoin:
        """创建用户金币账户"""
        user_coin = UserCoin(
            user_id=user_id,
            total_coins=total_coins,
            available_coins=available_coins,
            frozen_coins=frozen_coins
        )
        self.session.add(user_coin)
        self.session.flush()
        return user_coin
    
    def update_user_coin(self, user_id: int, **kwargs) -> Optional[UserCoin]:
        """更新用户金币账户"""
        user_coin = self.get_user_coin(user_id)
        if user_coin:
            for key, value in kwargs.items():
                if hasattr(user_coin, key):
                    setattr(user_coin, key, value)
            self.session.flush()
        return user_coin
    
    # CoinTransaction 相关方法
    def get_user_transactions(self, user_id: int, limit: int = 10) -> List[CoinTransaction]:
        """获取用户交易记录"""
        return (self.session.query(CoinTransaction)
                .filter(CoinTransaction.user_id == user_id)
                .order_by(desc(CoinTransaction.created_at))
                .limit(limit)
                .all())
    
    def get_user_transactions_paginated(self, user_id: int, page: int = 1, per_page: int = 20):
        """获取用户交易记录（分页）"""
        return (self.session.query(CoinTransaction)
                .filter(CoinTransaction.user_id == user_id)
                .order_by(desc(CoinTransaction.created_at))
                .paginate(page=page, per_page=per_page, error_out=False))
    
    def create_transaction(self, **kwargs) -> CoinTransaction:
        """创建交易记录"""
        transaction = CoinTransaction(**kwargs)
        self.session.add(transaction)
        self.session.flush()
        return transaction
    
    # CoinPackage 相关方法
    def get_active_packages(self) -> List[CoinPackage]:
        """获取启用的金币套餐"""
        return (self.session.query(CoinPackage)
                .filter(CoinPackage.is_active == True)
                .order_by(CoinPackage.sort_order, CoinPackage.price)
                .all())
    
    def get_package(self, package_id: int) -> Optional[CoinPackage]:
        """获取金币套餐"""
        return self.session.query(CoinPackage).filter(CoinPackage.id == package_id).first()
    
    def create_package(self, **kwargs) -> CoinPackage:
        """创建金币套餐"""
        package = CoinPackage(**kwargs)
        self.session.add(package)
        self.session.flush()
        return package
    
    # CoinOrder 相关方法
    def get_coin_order(self, order_id: int) -> Optional[CoinOrder]:
        """获取金币订单"""
        return self.session.query(CoinOrder).filter(CoinOrder.id == order_id).first()
    
    def get_coin_order_by_no(self, order_no: str) -> Optional[CoinOrder]:
        """根据订单号获取金币订单"""
        return self.session.query(CoinOrder).filter(CoinOrder.order_no == order_no).first()
    
    def create_coin_order(self, **kwargs) -> CoinOrder:
        """创建金币订单"""
        order = CoinOrder(**kwargs)
        self.session.add(order)
        self.session.flush()
        return order
    
    def update_coin_order(self, order_id: int, **kwargs) -> Optional[CoinOrder]:
        """更新金币订单"""
        order = self.get_coin_order(order_id)
        if order:
            for key, value in kwargs.items():
                if hasattr(order, key):
                    setattr(order, key, value)
            self.session.flush()
        return order
    
    def get_user_orders(self, user_id: int, page: int = 1, per_page: int = 20):
        """获取用户订单（分页）"""
        return (self.session.query(CoinOrder)
                .filter(CoinOrder.user_id == user_id)
                .order_by(desc(CoinOrder.created_at))
                .paginate(page=page, per_page=per_page, error_out=False))
    
    # DailyBonus 相关方法
    def get_daily_bonus(self, user_id: int, bonus_date: date) -> Optional[DailyBonus]:
        """获取每日签到记录"""
        return (self.session.query(DailyBonus)
                .filter(and_(
                    DailyBonus.user_id == user_id,
                    DailyBonus.bonus_date == bonus_date
                ))
                .first())
    
    def create_daily_bonus(self, **kwargs) -> DailyBonus:
        """创建每日签到记录"""
        bonus = DailyBonus(**kwargs)
        self.session.add(bonus)
        self.session.commit()
        return bonus
    
    def get_user_bonus_stats(self, user_id: int) -> dict:
        """获取用户签到统计"""
        # 总签到天数
        total_days = (self.session.query(func.count(DailyBonus.id))
                     .filter(DailyBonus.user_id == user_id)
                     .scalar() or 0)
        
        # 连续签到天数
        streak_days = 0
        today = date.today()
        for i in range(30):  # 最多查找30天
            check_date = today - timedelta(days=i)
            bonus = self.get_daily_bonus(user_id, check_date)
            if bonus:
                streak_days += 1
            else:
                break
        
        # 本月签到天数
        month_start = today.replace(day=1)
        month_days = (self.session.query(func.count(DailyBonus.id))
                     .filter(and_(
                         DailyBonus.user_id == user_id,
                         DailyBonus.bonus_date >= month_start
                     ))
                     .scalar() or 0)
        
        return {
            'total_days': total_days,
            'streak_days': streak_days,
            'month_days': month_days
        }
    
    # 统计方法
    def get_coin_statistics(self) -> dict:
        """获取金币系统统计"""
        # 总用户数（有金币账户的）
        total_users = self.session.query(func.count(UserCoin.id)).scalar() or 0
        
        # 总金币发行量
        total_coins_issued = (self.session.query(func.sum(CoinTransaction.amount))
                            .filter(CoinTransaction.amount > 0)
                            .scalar() or 0)
        
        # 总金币消耗量
        total_coins_spent = (self.session.query(func.sum(func.abs(CoinTransaction.amount)))
                           .filter(CoinTransaction.amount < 0)
                           .scalar() or 0)
        
        # 今日新增用户
        today = date.today()
        today_new_users = (self.session.query(func.count(UserCoin.id))
                          .filter(func.date(UserCoin.created_at) == today)
                          .scalar() or 0)
        
        # 今日签到用户数
        today_bonus_users = (self.session.query(func.count(DailyBonus.id))
                           .filter(DailyBonus.bonus_date == today)
                           .scalar() or 0)
        
        return {
            'total_users': total_users,
            'total_coins_issued': total_coins_issued or 0,
            'total_coins_spent': total_coins_spent or 0,
            'today_new_users': today_new_users,
            'today_bonus_users': today_bonus_users
        }