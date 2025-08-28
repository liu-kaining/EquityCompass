"""
数据模型包
"""
from .user import User, UserPlan
from .stock import Stock, UserWatchlist
from .analysis import AnalysisTask, PromptTemplate, ReportIndex, ReportStatistics, ReportViewLog, ReportDownloadLog
from .email import EmailSubscription
from .payment import PaymentTransaction
from .admin import Admin, SystemConfig

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
    'PaymentTransaction',
    'Admin',
    'SystemConfig',
]
