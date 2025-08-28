"""
报告统计API
"""
import logging
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services.data.report_statistics_service import ReportStatisticsService
from app.utils.response import success_response, error_response

logger = logging.getLogger(__name__)

# 创建蓝图
report_statistics_bp = Blueprint('report_statistics', __name__, url_prefix='/api/report-statistics')


@report_statistics_bp.route('/record-view', methods=['POST'])
@login_required
def record_view():
    """记录报告浏览"""
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        
        if not report_id:
            return error_response('报告ID不能为空')
        
        # 获取请求信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        referer = request.headers.get('Referer')
        view_duration = data.get('view_duration')
        
        # 记录浏览
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            success = service.record_view(
                report_id=report_id,
                user_id=current_user.id if current_user else None,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer,
                view_duration=view_duration
            )
        
        if success:
            return success_response('浏览记录成功')
        else:
            return error_response('浏览记录失败')
            
    except Exception as e:
        logger.error(f"记录报告浏览失败: {str(e)}")
        return error_response('服务器错误')


@report_statistics_bp.route('/record-download', methods=['POST'])
@login_required
def record_download():
    """记录报告下载"""
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        download_format = data.get('format', 'PDF')
        file_size = data.get('file_size')
        
        if not report_id:
            return error_response('报告ID不能为空')
        
        # 获取请求信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # 记录下载
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            success = service.record_download(
                report_id=report_id,
                user_id=current_user.id if current_user else None,
                ip_address=ip_address,
                user_agent=user_agent,
                download_format=download_format,
                file_size=file_size
            )
        
        if success:
            return success_response('下载记录成功')
        else:
            return error_response('下载记录失败')
            
    except Exception as e:
        logger.error(f"记录报告下载失败: {str(e)}")
        return error_response('服务器错误')


@report_statistics_bp.route('/record-share', methods=['POST'])
@login_required
def record_share():
    """记录报告分享"""
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        
        if not report_id:
            return error_response('报告ID不能为空')
        
        # 记录分享
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            success = service.record_share(report_id=report_id)
        
        if success:
            return success_response('分享记录成功')
        else:
            return error_response('分享记录失败')
            
    except Exception as e:
        logger.error(f"记录报告分享失败: {str(e)}")
        return error_response('服务器错误')


@report_statistics_bp.route('/record-favorite', methods=['POST'])
@login_required
def record_favorite():
    """记录报告收藏"""
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        
        if not report_id:
            return error_response('报告ID不能为空')
        
        # 记录收藏
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            success = service.record_favorite(report_id=report_id)
        
        if success:
            return success_response('收藏记录成功')
        else:
            return error_response('收藏记录失败')
            
    except Exception as e:
        logger.error(f"记录报告收藏失败: {str(e)}")
        return error_response('服务器错误')


@report_statistics_bp.route('/report/<int:report_id>', methods=['GET'])
def get_report_statistics(report_id):
    """获取报告统计信息"""
    try:
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            statistics = service.get_report_statistics(report_id)
        
        if statistics:
            return success_response('获取成功', data=statistics)
        else:
            return error_response('报告统计信息不存在')
            
    except Exception as e:
        logger.error(f"获取报告统计失败: {str(e)}")
        return error_response('服务器错误')


@report_statistics_bp.route('/popular', methods=['GET'])
def get_popular_reports():
    """获取热门报告"""
    try:
        limit = request.args.get('limit', 10, type=int)
        days = request.args.get('days', 30, type=int)
        
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            popular_reports = service.get_popular_reports(limit=limit, days=days)
        
        return success_response('获取成功', data=popular_reports)
        
    except Exception as e:
        logger.error(f"获取热门报告失败: {str(e)}")
        return error_response('服务器错误')


@report_statistics_bp.route('/user-stats', methods=['GET'])
@login_required
def get_user_statistics():
    """获取用户统计信息"""
    try:
        days = request.args.get('days', 30, type=int)
        
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            user_stats = service.get_user_statistics(
                user_id=current_user.id,
                days=days
            )
        
        return success_response('获取成功', data=user_stats)
        
    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        return error_response('服务器错误')


@report_statistics_bp.route('/global-stats', methods=['GET'])
def get_global_statistics():
    """获取全局统计信息"""
    try:
        days = request.args.get('days', 30, type=int)
        
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            global_stats = service.get_global_statistics(days=days)
        
        return success_response('获取成功', data=global_stats)
        
    except Exception as e:
        logger.error(f"获取全局统计失败: {str(e)}")
        return error_response('服务器错误')


@report_statistics_bp.route('/daily-stats', methods=['GET'])
def get_daily_statistics():
    """获取每日统计信息"""
    try:
        days = request.args.get('days', 7, type=int)
        
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            daily_stats = service.get_daily_statistics(days=days)
        
        return success_response('获取成功', data=daily_stats)
        
    except Exception as e:
        logger.error(f"获取每日统计失败: {str(e)}")
        return error_response('服务器错误')
