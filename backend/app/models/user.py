"""
用户相关数据模型
"""
from app import db
from datetime import datetime
from sqlalchemy import func


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, comment='邮箱地址，唯一标识')
    nickname = db.Column(db.String(100), comment='用户昵称')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, comment='账户是否激活')
    
    # 关系
    plans = db.relationship('UserPlan', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    watchlist = db.relationship('UserWatchlist', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    analysis_tasks = db.relationship('AnalysisTask', backref='user', lazy='dynamic')
    email_subscription = db.relationship('EmailSubscription', backref='user', uselist=False, cascade='all, delete-orphan')
    payment_transactions = db.relationship('PaymentTransaction', backref='user', lazy='dynamic')
    custom_stocks = db.relationship('Stock', backref='creator', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'email': self.email,
            'nickname': self.nickname,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }


class UserPlan(db.Model):
    """用户计划表"""
    __tablename__ = 'user_plans'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False, comment='TRIAL/FREE/SUBSCRIPTION/PAY_PER_USE')
    plan_start_date = db.Column(db.DateTime)
    plan_end_date = db.Column(db.DateTime)
    remaining_quota = db.Column(db.Integer, default=0, comment='剩余分析次数')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPlan {self.user_id}:{self.plan_type}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'plan_type': self.plan_type,
            'plan_start_date': self.plan_start_date.isoformat() if self.plan_start_date else None,
            'plan_end_date': self.plan_end_date.isoformat() if self.plan_end_date else None,
            'remaining_quota': self.remaining_quota,
            'is_active': self.is_active
        }
