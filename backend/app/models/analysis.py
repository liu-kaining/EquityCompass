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
    
    # 关系
    statistics = db.relationship('ReportStatistics', backref='report', uselist=False)
    
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
            'stock': self.stock.to_dict() if self.stock else None,
            'statistics': self.statistics.to_dict() if self.statistics else None
        }


class ReportStatistics(db.Model):
    """报告统计表"""
    __tablename__ = 'report_statistics'
    
    id = db.Column(db.BigInteger, primary_key=True)
    report_id = db.Column(db.BigInteger, db.ForeignKey('report_index.id'), nullable=False, unique=True)
    view_count = db.Column(db.Integer, default=0, comment='浏览次数')
    download_count = db.Column(db.Integer, default=0, comment='下载次数')
    share_count = db.Column(db.Integer, default=0, comment='分享次数')
    favorite_count = db.Column(db.Integer, default=0, comment='收藏次数')
    last_viewed_at = db.Column(db.DateTime, comment='最后浏览时间')
    last_downloaded_at = db.Column(db.DateTime, comment='最后下载时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ReportStatistics {self.report_id}:{self.view_count}views>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'view_count': self.view_count,
            'download_count': self.download_count,
            'share_count': self.share_count,
            'favorite_count': self.favorite_count,
            'last_viewed_at': self.last_viewed_at.isoformat() if self.last_viewed_at else None,
            'last_downloaded_at': self.last_downloaded_at.isoformat() if self.last_downloaded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def increment_view(self):
        """增加浏览次数"""
        self.view_count += 1
        self.last_viewed_at = datetime.utcnow()
        db.session.commit()
    
    def increment_download(self):
        """增加下载次数"""
        self.download_count += 1
        self.last_downloaded_at = datetime.utcnow()
        db.session.commit()
    
    def increment_share(self):
        """增加分享次数"""
        self.share_count += 1
        db.session.commit()
    
    def increment_favorite(self):
        """增加收藏次数"""
        self.favorite_count += 1
        db.session.commit()


class ReportViewLog(db.Model):
    """报告浏览日志表"""
    __tablename__ = 'report_view_logs'
    
    id = db.Column(db.BigInteger, primary_key=True)
    report_id = db.Column(db.BigInteger, db.ForeignKey('report_index.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True, comment='用户ID，可为空（匿名浏览）')
    ip_address = db.Column(db.String(45), comment='IP地址')
    user_agent = db.Column(db.String(500), comment='用户代理')
    referer = db.Column(db.String(500), comment='来源页面')
    view_duration = db.Column(db.Integer, comment='浏览时长（秒）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    report = db.relationship('ReportIndex', backref='view_logs')
    user = db.relationship('User', backref='report_views')
    
    def __repr__(self):
        return f'<ReportViewLog {self.report_id}:{self.user_id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referer': self.referer,
            'view_duration': self.view_duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ReportDownloadLog(db.Model):
    """报告下载日志表"""
    __tablename__ = 'report_download_logs'
    
    id = db.Column(db.BigInteger, primary_key=True)
    report_id = db.Column(db.BigInteger, db.ForeignKey('report_index.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True, comment='用户ID，可为空（匿名下载）')
    ip_address = db.Column(db.String(45), comment='IP地址')
    user_agent = db.Column(db.String(500), comment='用户代理')
    download_format = db.Column(db.String(20), comment='下载格式：PDF/ZIP')
    file_size = db.Column(db.BigInteger, comment='文件大小（字节）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    report = db.relationship('ReportIndex', backref='download_logs')
    user = db.relationship('User', backref='report_downloads')
    
    def __repr__(self):
        return f'<ReportDownloadLog {self.report_id}:{self.download_format}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'download_format': self.download_format,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
