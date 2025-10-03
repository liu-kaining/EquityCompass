"""
用户相关数据模型
"""
from app import db
from datetime import datetime
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名，唯一标识')
    email = db.Column(db.String(255), unique=True, nullable=False, comment='邮箱地址，必填但暂不验证')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    nickname = db.Column(db.String(100), comment='用户昵称')
    plan_type = db.Column(db.String(50), default='TRIAL', comment='TRIAL/FREE/SUBSCRIPTION/PAY_PER_USE')
    remaining_quota = db.Column(db.Integer, default=1, comment='剩余分析次数')
    user_role = db.Column(db.String(20), default='USER', comment='用户角色：SUPER_ADMIN/SITE_ADMIN/USER')
    last_login = db.Column(db.DateTime, comment='最后登录时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, comment='账户是否激活')
    email_verified = db.Column(db.Boolean, default=False, comment='邮箱是否已验证')
    
    # 关系
    plans = db.relationship('UserPlan', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    watchlist = db.relationship('UserWatchlist', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    analysis_tasks = db.relationship('AnalysisTask', backref='user', lazy='dynamic')
    email_subscription = db.relationship('EmailSubscription', backref='user', uselist=False, cascade='all, delete-orphan')
    payment_transactions = db.relationship('PaymentTransaction', backref='user', lazy='dynamic')
    custom_stocks = db.relationship('Stock', backref='creator', lazy='dynamic')
    # 金币系统关系（通过backref自动创建，不需要重复定义）
    # coin_account 通过 UserCoin 模型的 backref 自动创建
    # coin_transactions, coin_orders, daily_bonuses 通过各自模型的 backref 自动创建
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_super_admin(self):
        """是否为超级管理员"""
        return self.user_role == 'SUPER_ADMIN'
    
    def is_site_admin(self):
        """是否为网站管理员"""
        return self.user_role == 'SITE_ADMIN'
    
    def is_admin(self):
        """是否为管理员（超级管理员或网站管理员）"""
        return self.user_role in ['SUPER_ADMIN', 'SITE_ADMIN']
    
    def can_manage_users(self):
        """是否可以管理用户"""
        return self.user_role == 'SUPER_ADMIN'
    
    def can_view_all_reports(self):
        """是否可以查看所有报告"""
        return self.user_role in ['SUPER_ADMIN', 'SITE_ADMIN']
    
    def can_download_all_reports(self):
        """是否可以下载所有报告"""
        return self.user_role in ['SUPER_ADMIN', 'SITE_ADMIN']
    
    def can_view_statistics(self):
        """是否可以查看统计页面"""
        return self.user_role in ['SUPER_ADMIN', 'SITE_ADMIN']
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname,
            'plan_type': self.plan_type,
            'remaining_quota': self.remaining_quota,
            'user_role': self.user_role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'email_verified': self.email_verified
        }


class UserPlan(db.Model):
    """用户计划表"""
    __tablename__ = 'user_plans'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
