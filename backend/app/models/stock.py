"""
股票相关数据模型
"""
from app import db
from datetime import datetime


class Stock(db.Model):
    """股票表"""
    __tablename__ = 'stocks'
    
    id = db.Column(db.BigInteger, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, comment='股票代码，如AAPL或00700.HK')
    name = db.Column(db.String(200), nullable=False, comment='公司名称')
    market = db.Column(db.String(10), nullable=False, comment='US/HK')
    exchange = db.Column(db.String(50), comment='NASDAQ/HKEX等')
    industry = db.Column(db.String(100), comment='行业分类')
    stock_type = db.Column(db.String(20), default='BUILT_IN', comment='BUILT_IN/USER_CUSTOM')
    created_by_user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), comment='自定义股票的创建者')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    watchlist_items = db.relationship('UserWatchlist', backref='stock', lazy='dynamic', cascade='all, delete-orphan')
    analysis_tasks = db.relationship('AnalysisTask', backref='stock', lazy='dynamic')
    reports = db.relationship('ReportIndex', backref='stock', lazy='dynamic')
    
    def __repr__(self):
        return f'<Stock {self.code}:{self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'market': self.market,
            'exchange': self.exchange,
            'industry': self.industry,
            'stock_type': self.stock_type,
            'created_by_user_id': self.created_by_user_id
        }


class UserWatchlist(db.Model):
    """用户关注列表"""
    __tablename__ = 'user_watchlists'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.BigInteger, db.ForeignKey('stocks.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唐一约束
    __table_args__ = (db.UniqueConstraint('user_id', 'stock_id'),)
    
    def __repr__(self):
        return f'<UserWatchlist {self.user_id}:{self.stock_id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'stock_id': self.stock_id,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'stock': self.stock.to_dict() if self.stock else None
        }
