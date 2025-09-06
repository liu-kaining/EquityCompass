"""
AI模型配置数据模型
"""
from app import db
from datetime import datetime
from sqlalchemy import JSON


class AIConfig(db.Model):
    """AI模型配置表"""
    __tablename__ = 'ai_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(50), nullable=False, unique=True, comment='提供商名称')
    display_name = db.Column(db.String(100), nullable=False, comment='显示名称')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认配置')
    
    # 基础配置
    api_key = db.Column(db.Text, nullable=False, comment='API密钥')
    model_name = db.Column(db.String(100), nullable=False, comment='模型名称')
    api_url = db.Column(db.String(500), comment='API地址')
    
    # 高级配置（JSON格式存储）
    advanced_config = db.Column(JSON, comment='高级配置参数')
    
    # 使用统计
    total_requests = db.Column(db.Integer, default=0, comment='总请求次数')
    successful_requests = db.Column(db.Integer, default=0, comment='成功请求次数')
    failed_requests = db.Column(db.Integer, default=0, comment='失败请求次数')
    last_used_at = db.Column(db.DateTime, comment='最后使用时间')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='创建者ID')
    
    def __repr__(self):
        return f'<AIConfig {self.provider_name}: {self.display_name}>'
    
    def to_dict(self, include_sensitive=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'provider_name': self.provider_name,
            'display_name': self.display_name,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'model_name': self.model_name,
            'api_url': self.api_url,
            'advanced_config': self.advanced_config or {},
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.get_success_rate(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by
        }
        
        # 只有在需要时才包含敏感信息
        if include_sensitive:
            data['api_key'] = self.api_key
        
        return data
    
    def get_success_rate(self):
        """获取成功率"""
        if self.total_requests == 0:
            return 0.0
        return round((self.successful_requests / self.total_requests) * 100, 2)
    
    def get_config_dict(self):
        """获取配置字典，用于LLM Provider"""
        config = {
            'name': self.provider_name,
            'api_key': self.api_key,
            'model': self.model_name,
            'api_url': self.api_url,
            'is_active': self.is_active
        }
        
        # 合并高级配置
        if self.advanced_config:
            config.update(self.advanced_config)
        
        return config
    
    def update_usage_stats(self, success=True):
        """更新使用统计"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.last_used_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def get_active_configs():
        """获取所有激活的配置"""
        return AIConfig.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_default_config():
        """获取默认配置"""
        return AIConfig.query.filter_by(is_default=True, is_active=True).first()
    
    @staticmethod
    def set_default_config(config_id):
        """设置默认配置"""
        # 先清除所有默认标记
        AIConfig.query.update({'is_default': False})
        
        # 设置新的默认配置
        config = AIConfig.query.get(config_id)
        if config:
            config.is_default = True
            db.session.commit()
            return True
        return False
