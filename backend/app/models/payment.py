"""
支付相关数据模型
"""
from app import db
from datetime import datetime
# 暂时移除PostgreSQL特定的JSON类型，使用Text代替


class PaymentTransaction(db.Model):
    """支付交易表"""
    __tablename__ = 'payment_transactions'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    transaction_id = db.Column(db.String(255), unique=True, nullable=False, comment='第三方支付ID')
    payment_provider = db.Column(db.String(50), nullable=False, comment='STRIPE/PADDLE')
    amount = db.Column(db.Numeric(10, 2), nullable=False, comment='金额')
    currency = db.Column(db.String(3), default='USD', comment='货币类型')
    transaction_type = db.Column(db.String(50), nullable=False, comment='SUBSCRIPTION/ONE_TIME')
    status = db.Column(db.String(20), default='PENDING', comment='PENDING/SUCCESS/FAILED/REFUNDED')
    raw_response = db.Column(db.Text, comment='支付网关原始响应')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PaymentTransaction {self.transaction_id}:{self.status}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'payment_provider': self.payment_provider,
            'amount': float(self.amount) if self.amount else 0,
            'currency': self.currency,
            'transaction_type': self.transaction_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
