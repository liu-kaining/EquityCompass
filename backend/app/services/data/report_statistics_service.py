"""
报告统计服务
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.analysis import ReportIndex, ReportStatistics, ReportViewLog, ReportDownloadLog
from app.models.user import User

logger = logging.getLogger(__name__)


class ReportStatisticsService:
    """报告统计服务"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_or_create_statistics(self, report_id: int) -> ReportStatistics:
        """获取或创建报告统计记录"""
        statistics = self.session.query(ReportStatistics).filter_by(report_id=report_id).first()
        if not statistics:
            statistics = ReportStatistics(report_id=report_id)
            self.session.add(statistics)
            self.session.commit()
        return statistics
    
    def record_view(self, report_id: int, user_id: Optional[int] = None, 
                   ip_address: str = None, user_agent: str = None, 
                   referer: str = None, view_duration: int = None) -> bool:
        """记录报告浏览"""
        try:
            # 更新统计
            statistics = self.get_or_create_statistics(report_id)
            statistics.increment_view()
            
            # 记录浏览日志
            view_log = ReportViewLog(
                report_id=report_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer,
                view_duration=view_duration
            )
            self.session.add(view_log)
            self.session.commit()
            
            logger.info(f"记录报告浏览 - 报告ID: {report_id}, 用户ID: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"记录报告浏览失败: {str(e)}")
            self.session.rollback()
            return False
    
    def record_download(self, report_id: int, user_id: Optional[int] = None,
                       ip_address: str = None, user_agent: str = None,
                       download_format: str = None, file_size: int = None) -> bool:
        """记录报告下载"""
        try:
            # 更新统计
            statistics = self.get_or_create_statistics(report_id)
            statistics.increment_download()
            
            # 记录下载日志
            download_log = ReportDownloadLog(
                report_id=report_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                download_format=download_format,
                file_size=file_size
            )
            self.session.add(download_log)
            self.session.commit()
            
            logger.info(f"记录报告下载 - 报告ID: {report_id}, 用户ID: {user_id}, 格式: {download_format}")
            return True
            
        except Exception as e:
            logger.error(f"记录报告下载失败: {str(e)}")
            self.session.rollback()
            return False
    
    def record_share(self, report_id: int) -> bool:
        """记录报告分享"""
        try:
            statistics = self.get_or_create_statistics(report_id)
            statistics.increment_share()
            logger.info(f"记录报告分享 - 报告ID: {report_id}")
            return True
            
        except Exception as e:
            logger.error(f"记录报告分享失败: {str(e)}")
            return False
    
    def record_favorite(self, report_id: int) -> bool:
        """记录报告收藏"""
        try:
            statistics = self.get_or_create_statistics(report_id)
            statistics.increment_favorite()
            logger.info(f"记录报告收藏 - 报告ID: {report_id}")
            return True
            
        except Exception as e:
            logger.error(f"记录报告收藏失败: {str(e)}")
            return False
    
    def get_report_statistics(self, report_id: int) -> Optional[Dict[str, Any]]:
        """获取报告统计信息"""
        try:
            statistics = self.session.query(ReportStatistics).filter_by(report_id=report_id).first()
            if statistics:
                return statistics.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"获取报告统计失败: {str(e)}")
            return None
    
    def get_popular_reports(self, limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
        """获取热门报告"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 按浏览次数排序
            popular_reports = self.session.query(
                ReportIndex,
                ReportStatistics.view_count,
                ReportStatistics.download_count
            ).join(ReportStatistics).filter(
                ReportIndex.generated_at >= start_date
            ).order_by(
                desc(ReportStatistics.view_count)
            ).limit(limit).all()
            
            result = []
            for report, view_count, download_count in popular_reports:
                report_dict = report.to_dict()
                report_dict['view_count'] = view_count
                report_dict['download_count'] = download_count
                result.append(report_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"获取热门报告失败: {str(e)}")
            return []
    
    def get_user_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 用户浏览的报告数
            viewed_reports = self.session.query(func.count(ReportViewLog.report_id.distinct())).filter(
                ReportViewLog.user_id == user_id,
                ReportViewLog.created_at >= start_date
            ).scalar()
            
            # 用户下载的报告数
            downloaded_reports = self.session.query(func.count(ReportDownloadLog.report_id.distinct())).filter(
                ReportDownloadLog.user_id == user_id,
                ReportDownloadLog.created_at >= start_date
            ).scalar()
            
            # 用户总浏览次数
            total_views = self.session.query(func.count(ReportViewLog.id)).filter(
                ReportViewLog.user_id == user_id,
                ReportViewLog.created_at >= start_date
            ).scalar()
            
            # 用户总下载次数
            total_downloads = self.session.query(func.count(ReportDownloadLog.id)).filter(
                ReportDownloadLog.user_id == user_id,
                ReportDownloadLog.created_at >= start_date
            ).scalar()
            
            return {
                'viewed_reports': viewed_reports or 0,
                'downloaded_reports': downloaded_reports or 0,
                'total_views': total_views or 0,
                'total_downloads': total_downloads or 0,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {str(e)}")
            return {}
    
    def get_global_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取全局统计信息"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 总报告数
            total_reports = self.session.query(func.count(ReportIndex.id)).filter(
                ReportIndex.generated_at >= start_date
            ).scalar()
            
            # 总浏览次数
            total_views = self.session.query(func.sum(ReportStatistics.view_count)).join(ReportIndex).filter(
                ReportIndex.generated_at >= start_date
            ).scalar()
            
            # 总下载次数
            total_downloads = self.session.query(func.sum(ReportStatistics.download_count)).join(ReportIndex).filter(
                ReportIndex.generated_at >= start_date
            ).scalar()
            
            # 总分享次数
            total_shares = self.session.query(func.sum(ReportStatistics.share_count)).join(ReportIndex).filter(
                ReportIndex.generated_at >= start_date
            ).scalar()
            
            # 总收藏次数
            total_favorites = self.session.query(func.sum(ReportStatistics.favorite_count)).join(ReportIndex).filter(
                ReportIndex.generated_at >= start_date
            ).scalar()
            
            return {
                'total_reports': total_reports or 0,
                'total_views': total_views or 0,
                'total_downloads': total_downloads or 0,
                'total_shares': total_shares or 0,
                'total_favorites': total_favorites or 0,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"获取全局统计失败: {str(e)}")
            return {}
    
    def get_daily_statistics(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取每日统计信息"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 按日期分组统计
            daily_stats = self.session.query(
                func.date(ReportViewLog.created_at).label('date'),
                func.count(ReportViewLog.id).label('views'),
                func.count(ReportDownloadLog.id).label('downloads')
            ).outerjoin(ReportDownloadLog, 
                       func.date(ReportViewLog.created_at) == func.date(ReportDownloadLog.created_at)
            ).filter(
                ReportViewLog.created_at >= start_date
            ).group_by(
                func.date(ReportViewLog.created_at)
            ).order_by(
                func.date(ReportViewLog.created_at)
            ).all()
            
            result = []
            for date, views, downloads in daily_stats:
                result.append({
                    'date': date.isoformat(),
                    'views': views or 0,
                    'downloads': downloads or 0
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取每日统计失败: {str(e)}")
            return []
