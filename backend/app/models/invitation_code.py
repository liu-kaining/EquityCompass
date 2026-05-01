"""
邀请码相关数据模型
"""
from app import db
from datetime import datetime
from sqlalchemy import Index


class InvitationCode(db.Model):
    """邀请码表"""
    __tablename__ = 'invitation_codes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(18), unique=True, nullable=False, comment='邀请码内容，18个字符')
    code_type = db.Column(db.String(20), default='INVITATION', nullable=False, comment='码类型：INVITATION/RECHARGE')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者（管理员ID）')
    is_used = db.Column(db.Boolean, default=False, nullable=False, comment='是否已使用')
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='使用者ID')
    used_at = db.Column(db.DateTime, nullable=True, comment='使用时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    
    # 关系
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_invitation_codes', lazy='select')
    user = db.relationship('User', foreign_keys=[used_by], backref='used_invitation_code', uselist=False, lazy='select')
    
    # 索引
    __table_args__ = (
        Index('idx_code_type', 'code_type'),
        Index('idx_is_used', 'is_used'),
        Index('idx_created_by', 'created_by'),
        Index('idx_used_by', 'used_by'),
    )
    
    def __repr__(self):
        return f'<InvitationCode {self.code[:8]}... {"已使用" if self.is_used else "未使用"}>'
    
    def to_dict(self, include_user=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'code': self.code,
            'code_display': self.format_display(),  # 格式化显示
            'code_type': self.code_type,
            'created_by': self.created_by,
            'creator_username': self.creator.username if self.creator else None,
            'is_used': self.is_used,
            'used_by': self.used_by,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'created_at': self.user.created_at.isoformat() if self.user.created_at else None,
            }
        
        return data
    
    def format_display(self):
        """格式化显示邀请码（分组显示）"""
        # 18个字符分组：6-6-6
        code = self.code.replace('-', '').replace(' ', '')  # 去除可能的分隔符
        if len(code) == 18:
            return f"{code[0:6]}-{code[6:12]}-{code[12:18]}"
        return code
    
    @staticmethod
    def normalize_code(code):
        """标准化邀请码（去除分隔符和空格，保持原始大小写）"""
        if not code:
            return None
        # 去除分隔符和空格，但保持大小写（因为邀请码区分大小写）
        return code.replace('-', '').replace(' ', '').replace('_', '').strip()

