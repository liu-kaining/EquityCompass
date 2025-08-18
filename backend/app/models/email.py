"""
邮件相关数据模型
"""
from app import db
from datetime import datetime


class EmailSubscription(db.Model):
    """邮件订阅表"""
    __tablename__ = 'email_subscriptions'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), unique=True, nullable=False)
    is_subscribed = db.Column(db.Boolean, default=True, comment='是否订阅每日邮件')
    frequency = db.Column(db.String(20), default='DAILY', comment='发送频率')
    last_sent_at = db.Column(db.DateTime, comment='最后发送时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailSubscription {self.user_id}:{self.is_subscribed}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'is_subscribed': self.is_subscribed,
            'frequency': self.frequency,
            'last_sent_at': self.last_sent_at.isoformat() if self.last_sent_at else None
        }
