"""
数据模型包
"""
from .user import User, UserPlan
from .stock import Stock, UserWatchlist
from .analysis import AnalysisTask, PromptTemplate, ReportIndex, ReportStatistics, ReportViewLog, ReportDownloadLog
from .email import EmailSubscription
# 注意：PaymentTransaction模型已删除（支付功能已移除）
from .admin import Admin, SystemConfig
from .invitation_code import InvitationCode

__all__ = [
    'User',
    'UserPlan', 
    'Stock',
    'UserWatchlist',
    'AnalysisTask',
    'PromptTemplate',
    'ReportIndex',
    'ReportStatistics',
    'ReportViewLog',
    'ReportDownloadLog',
    'EmailSubscription',
    # 'PaymentTransaction',  # 已删除
    'Admin',
    'SystemConfig',
    'InvitationCode',
]
