"""
提示词数据模型
"""
from app import db
from datetime import datetime
from sqlalchemy import JSON


class Prompt(db.Model):
    """提示词表"""
    __tablename__ = 'prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='提示词名称')
    description = db.Column(db.Text, comment='提示词描述')
    prompt_type = db.Column(db.String(50), nullable=False, comment='提示词类型：fundamental, technical')
    content = db.Column(db.Text, nullable=False, comment='提示词内容')
    version = db.Column(db.Integer, default=1, comment='版本号')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认版本')
    
    # 使用统计
    usage_count = db.Column(db.Integer, default=0, comment='使用次数')
    last_used_at = db.Column(db.DateTime, comment='最后使用时间')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='创建者ID')
    
    def __repr__(self):
        return f'<Prompt {self.name}: v{self.version}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'prompt_type': self.prompt_type,
            'content': self.content,
            'version': self.version,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by
        }
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def get_active_prompts_by_type(prompt_type: str):
        """获取指定类型的激活提示词"""
        return Prompt.query.filter_by(prompt_type=prompt_type, is_active=True).order_by(Prompt.is_default.desc(), Prompt.version.desc()).all()
    
    @staticmethod
    def get_default_prompt(prompt_type: str):
        """获取指定类型的默认提示词"""
        return Prompt.query.filter_by(prompt_type=prompt_type, is_default=True, is_active=True).first()
    
    @staticmethod
    def get_prompt_versions(name: str):
        """获取指定名称的所有版本"""
        return Prompt.query.filter_by(name=name).order_by(Prompt.version.desc()).all()
    
    @staticmethod
    def set_default_version(prompt_id: int):
        """设置默认版本"""
        prompt = Prompt.query.get(prompt_id)
        if not prompt:
            return False
        
        # 先清除同类型的所有默认标记
        Prompt.query.filter_by(prompt_type=prompt.prompt_type).update({'is_default': False})
        
        # 设置新的默认版本
        prompt.is_default = True
        db.session.commit()
        return True
    
    @staticmethod
    def get_latest_version(name: str):
        """获取指定名称的最新版本"""
        return Prompt.query.filter_by(name=name).order_by(Prompt.version.desc()).first()
    
    @staticmethod
    def create_new_version(name: str, prompt_type: str, content: str, description: str = None, created_by: int = None):
        """创建新版本"""
        # 获取当前最新版本号
        latest = Prompt.get_latest_version(name)
        new_version = (latest.version + 1) if latest else 1
        
        # 创建新版本
        new_prompt = Prompt(
            name=name,
            description=description,
            prompt_type=prompt_type,
            content=content,
            version=new_version,
            created_by=created_by
        )
        
        db.session.add(new_prompt)
        db.session.commit()
        return new_prompt
