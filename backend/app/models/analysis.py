"""
分析相关数据模型
"""
from app import db
from datetime import datetime, date


class AnalysisTask(db.Model):
    """分析任务表"""
    __tablename__ = 'analysis_tasks'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.BigInteger, db.ForeignKey('stocks.id'), nullable=False)
    task_id = db.Column(db.String(255), unique=True, nullable=False, comment='Celery任务ID')
    status = db.Column(db.String(20), default='PENDING', comment='PENDING/PROCESSING/SUCCESS/FAILED')
    analysis_date = db.Column(db.Date, nullable=False, comment='分析日期 YYYY-MM-DD')
    prompt_version = db.Column(db.String(50), comment='使用的Prompt版本')
    llm_model = db.Column(db.String(100), comment='使用的LLM模型')
    error_message = db.Column(db.Text, comment='失败时的错误信息')
    retry_count = db.Column(db.Integer, default=0, comment='重试次数')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, comment='完成时间')
    
    # 关系
    report = db.relationship('ReportIndex', backref='generated_by_task', uselist=False)
    
    def __repr__(self):
        return f'<AnalysisTask {self.task_id}:{self.status}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'status': self.status,
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
            'prompt_version': self.prompt_version,
            'llm_model': self.llm_model,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'stock': self.stock.to_dict() if self.stock else None
        }


class PromptTemplate(db.Model):
    """Prompt模板表"""
    __tablename__ = 'prompt_templates'
    
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(200), nullable=False, comment='模板名称')
    version = db.Column(db.String(50), nullable=False, comment='版本号')
    content = db.Column(db.Text, nullable=False, comment='Prompt内容')
    is_active = db.Column(db.Boolean, default=False, comment='是否为当前使用版本')
    template_type = db.Column(db.String(50), comment='TECHNICAL/FUNDAMENTAL/COMPREHENSIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 唐一约束
    __table_args__ = (db.UniqueConstraint('name', 'version'),)
    
    def __repr__(self):
        return f'<PromptTemplate {self.name}:{self.version}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'content': self.content,
            'is_active': self.is_active,
            'template_type': self.template_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ReportIndex(db.Model):
    """报告索引表"""
    __tablename__ = 'report_index'
    
    id = db.Column(db.BigInteger, primary_key=True)
    stock_id = db.Column(db.BigInteger, db.ForeignKey('stocks.id'), nullable=False)
    analysis_date = db.Column(db.Date, nullable=False, comment='分析日期 YYYY-MM-DD')
    file_path = db.Column(db.String(500), nullable=False, comment='JSON文件路径')
    summary = db.Column(db.Text, comment='报告摘要')
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    generated_by_task_id = db.Column(db.BigInteger, db.ForeignKey('analysis_tasks.id'))
    
    # 唐一约束
    __table_args__ = (db.UniqueConstraint('stock_id', 'analysis_date'),)
    
    def __repr__(self):
        return f'<ReportIndex {self.stock_id}:{self.analysis_date}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
            'file_path': self.file_path,
            'summary': self.summary,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'stock': self.stock.to_dict() if self.stock else None
        }
