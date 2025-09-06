"""
仪表板页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for
from app.utils.permissions import login_required, get_user_context

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """仪表板首页"""
    from app.services.data.stock_service import StockDataService
    from app.services.ai.analysis_service import AnalysisService
    from app import db
    
    # 获取用户上下文
    user_context = get_user_context()
    if not user_context:
        return redirect(url_for('auth.login'))
    
    user_id = user_context['user_id']
    is_admin = user_context['is_admin']
    
    # 获取真实数据
    stock_service = StockDataService(db.session)
    analysis_service = AnalysisService(db.session)
    
    # 获取关注列表数量
    watchlist_data = stock_service.get_user_watchlist(user_id)
    watchlist_count = watchlist_data['count']
    
    # 获取报告数量
    reports = analysis_service.get_user_reports(user_id, limit=100)
    reports_count = len(reports)
    
    # 根据用户角色获取不同的报告统计
    if is_admin:
        # 管理员：显示全局报告总数
        global_reports_count = analysis_service.get_global_reports_count()
        reports_count = global_reports_count
    else:
        # 普通用户：显示可访问的报告数量（基于关注列表）
        accessible_reports_count = analysis_service.get_user_accessible_reports_count(user_id)
        reports_count = accessible_reports_count
    
    user_data = {
        'email': user_context['email'],
        'username': user_context['username'],
        'nickname': user_context['nickname'],
        'user_role': user_context['user_role'],
        'watchlist_count': watchlist_count,
        'reports_count': reports_count,
        'plan_type': 'ADMIN' if is_admin else 'TRIAL',
        'remaining_quota': 999 if is_admin else 1,
        'is_admin': is_admin,
        'is_super_admin': user_context['is_super_admin'],
        'is_site_admin': user_context['is_site_admin'],
        'can_manage_users': user_context['can_manage_users'],
        'can_view_statistics': user_context['can_view_statistics']
    }
    return render_template('dashboard/index.html', user=user_data)
