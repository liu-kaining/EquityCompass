"""
报告统计API
"""
import logging
from flask import Blueprint, request, jsonify, current_app, session
from app.services.data.report_statistics_service import ReportStatisticsService
from app.utils.response import success_response, error_response

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

logger = logging.getLogger(__name__)

# 创建蓝图
report_statistics_bp = Blueprint('report_statistics', __name__, url_prefix='/api/report-statistics')


@report_statistics_bp.route('/record-view', methods=['POST'])
def record_view():
    """记录报告浏览"""
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        
        if not report_id:
            return error_response('INVALID_PARAM', '报告ID不能为空')
        
        # 获取请求信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        referer = request.headers.get('Referer')
        view_duration = data.get('view_duration')
        
        # 记录浏览
        with current_app.app_context():
            from app import db
            from flask import session
            service = ReportStatisticsService(db.session)
            success = service.record_view(
                report_id=report_id,
                user_id=session.get('user_id') if session.get('user_id') else None,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer,
                view_duration=view_duration
            )
        
        if success:
            return success_response(message='浏览记录成功')
        else:
            return error_response('OPERATION_FAILED', '浏览记录失败')
            
    except Exception as e:
        logger.error(f"记录报告浏览失败: {str(e)}")
        return error_response('INTERNAL_ERROR', '服务器错误')


@report_statistics_bp.route('/record-download', methods=['POST'])
def record_download():
    """记录报告下载"""
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        download_format = data.get('format', 'PDF')
        file_size = data.get('file_size')
        
        if not report_id:
            return error_response('INVALID_PARAM', '报告ID不能为空')
        
        # 获取请求信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # 记录下载
        with current_app.app_context():
            from app import db
            from flask import session
            service = ReportStatisticsService(db.session)
            success = service.record_download(
                report_id=report_id,
                user_id=session.get('user_id') if session.get('user_id') else None,
                ip_address=ip_address,
                user_agent=user_agent,
                download_format=download_format,
                file_size=file_size
            )
        
        if success:
            return success_response(message='下载记录成功')
        else:
            return error_response('OPERATION_FAILED', '下载记录失败')
            
    except Exception as e:
        logger.error(f"记录报告下载失败: {str(e)}")
        return error_response('INTERNAL_ERROR', '服务器错误')




@report_statistics_bp.route('/record-favorite', methods=['POST'])
def record_favorite():
    """记录报告收藏"""
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        
        if not report_id:
            return error_response('INVALID_PARAM', '报告ID不能为空')
        
        # 记录收藏
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            success = service.record_favorite(report_id=report_id)
        
        if success:
            return success_response(message='收藏记录成功')
        else:
            return error_response('OPERATION_FAILED', '收藏记录失败')
            
    except Exception as e:
        logger.error(f"记录报告收藏失败: {str(e)}")
        return error_response('INTERNAL_ERROR', '服务器错误')


@report_statistics_bp.route('/report/<int:report_id>', methods=['GET'])
def get_report_statistics(report_id):
    """获取报告统计信息"""
    try:
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            statistics = service.get_report_statistics(report_id)
        
        if statistics:
            return success_response(data=statistics, message='获取成功')
        else:
            return error_response('NOT_FOUND', '报告统计信息不存在')
            
    except Exception as e:
        logger.error(f"获取报告统计失败: {str(e)}")
        return error_response('INTERNAL_ERROR', '服务器错误')


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
        
        return success_response(data=popular_reports, message='获取成功')
        
    except Exception as e:
        logger.error(f"获取热门报告失败: {str(e)}")
        return error_response('INTERNAL_ERROR', '服务器错误')


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
                user_id=session.get('user_id'),
                days=days
            )
        
        return success_response(data=user_stats, message='获取成功')
        
    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        return error_response('INTERNAL_ERROR', '服务器错误')


@report_statistics_bp.route('/global-stats', methods=['GET'])
def get_global_statistics():
    """获取全局统计信息"""
    try:
        days = request.args.get('days', 30, type=int)
        
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            global_stats = service.get_global_statistics(days=days)
        
        return success_response(data=global_stats, message='获取成功')
        
    except Exception as e:
        logger.error(f"获取全局统计失败: {str(e)}")
        return error_response('INTERNAL_ERROR', '服务器错误')


@report_statistics_bp.route('/daily-stats', methods=['GET'])
def get_daily_statistics():
    """获取每日统计信息"""
    try:
        days = request.args.get('days', 7, type=int)
        
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            daily_stats = service.get_daily_statistics(days=days)
        
        return success_response(data=daily_stats, message='获取成功')
        
    except Exception as e:
        logger.error(f"获取每日统计失败: {str(e)}")
        return error_response('INTERNAL_ERROR', '服务器错误')


@report_statistics_bp.route('/clear-all', methods=['POST'])
@login_required
def clear_all_statistics():
    """清空所有统计数据（仅管理员）"""
    try:
        # 检查用户权限
        if not session.get('is_admin'):
            return error_response('PERMISSION_DENIED', '权限不足，只有管理员可以清空统计数据')
        
        with current_app.app_context():
            from app import db
            service = ReportStatisticsService(db.session)
            success = service.clear_all_statistics()
        
        if success:
            return success_response(message='所有统计数据已清空')
        else:
            return error_response('OPERATION_FAILED', '清空统计数据失败')
        
    except Exception as e:
        logger.error(f"清空统计数据失败: {str(e)}")
        return error_response('INTERNAL_ERROR', '服务器错误')
