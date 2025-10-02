"""
金币系统数据模型
"""
from datetime import datetime
from sqlalchemy import Index, UniqueConstraint
from app import db


class UserCoin(db.Model):
    """用户金币表"""
    __tablename__ = 'user_coins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    total_coins = db.Column(db.Integer, default=0, nullable=False)  # 总金币数
    available_coins = db.Column(db.Integer, default=0, nullable=False)  # 可用金币数
    frozen_coins = db.Column(db.Integer, default=0, nullable=False)  # 冻结金币数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='coin_account', uselist=False, lazy='select')
    transactions = db.relationship('CoinTransaction', backref='coin_account', lazy='dynamic')
    
    def __repr__(self):
        return f'<UserCoin user_id={self.user_id} available={self.available_coins}>'


class CoinTransaction(db.Model):
    """金币交易记录表"""
    __tablename__ = 'coin_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_coin_id = db.Column(db.Integer, db.ForeignKey('user_coins.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # EARN, SPEND, PURCHASE, REFUND, DAILY_BONUS
    amount = db.Column(db.Integer, nullable=False)  # 正数为获得，负数为消耗
    balance_before = db.Column(db.Integer, nullable=False)  # 交易前余额
    balance_after = db.Column(db.Integer, nullable=False)  # 交易后余额
    description = db.Column(db.String(255))  # 交易描述
    related_id = db.Column(db.Integer)  # 关联ID（如分析报告ID、订单ID等）
    related_type = db.Column(db.String(50))  # 关联类型（ANALYSIS, ORDER, BONUS等）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        Index('idx_user_transaction', 'user_id', 'created_at'),
        Index('idx_transaction_type', 'transaction_type'),
    )
    
    def __repr__(self):
        return f'<CoinTransaction user_id={self.user_id} type={self.transaction_type} amount={self.amount}>'


class CoinPackage(db.Model):
    """金币套餐表"""
    __tablename__ = 'coin_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 套餐名称
    description = db.Column(db.String(255))  # 套餐描述
    coins = db.Column(db.Integer, nullable=False)  # 金币数量
    price = db.Column(db.Float, nullable=False)  # 价格（元）
    original_price = db.Column(db.Float)  # 原价（用于显示折扣）
    package_type = db.Column(db.String(20), nullable=False)  # FREE, SMALL, MEDIUM, LARGE, XLARGE, SUBSCRIPTION
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    sort_order = db.Column(db.Integer, default=0)  # 排序
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CoinPackage {self.name} {self.coins}coins ¥{self.price}>'


class CoinOrder(db.Model):
    """金币订单表"""
    __tablename__ = 'coin_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('coin_packages.id'), nullable=False)
    order_no = db.Column(db.String(50), unique=True, nullable=False)  # 订单号
    amount = db.Column(db.Float, nullable=False)  # 订单金额
    coins = db.Column(db.Integer, nullable=False)  # 金币数量
    status = db.Column(db.String(20), default='PENDING')  # PENDING, PAID, CANCELLED, REFUNDED
    payment_method = db.Column(db.String(20))  # ALIPAY, WECHAT, STRIPE
    payment_id = db.Column(db.String(100))  # 第三方支付ID
    paid_at = db.Column(db.DateTime)  # 支付时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='coin_orders')
    package = db.relationship('CoinPackage', backref='orders')
    
    def __repr__(self):
        return f'<CoinOrder {self.order_no} {self.status}>'


class DailyBonus(db.Model):
    """每日签到奖励表"""
    __tablename__ = 'daily_bonuses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bonus_date = db.Column(db.Date, nullable=False)  # 奖励日期
    coins_earned = db.Column(db.Integer, nullable=False)  # 获得金币数
    streak_days = db.Column(db.Integer, default=1)  # 连续签到天数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束：每个用户每天只能签到一次
    __table_args__ = (
        UniqueConstraint('user_id', 'bonus_date', name='unique_daily_bonus'),
        Index('idx_user_bonus_date', 'user_id', 'bonus_date'),
    )
    
    def __repr__(self):
        return f'<DailyBonus user_id={self.user_id} date={self.bonus_date} coins={self.coins_earned}>'
