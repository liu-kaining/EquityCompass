"""
仪表板页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@dashboard_bp.route('/')
@login_required
def index():
    """仪表板首页"""
    from app.services.data.stock_service import StockDataService
    from app.services.ai.analysis_service import AnalysisService
    from app import db
    
    # 获取用户数据
    user_id = session.get('user_id')
    user_email = session.get('user_email', '')
    is_admin = session.get('is_admin', False)
    
    # 获取真实数据
    stock_service = StockDataService(db.session)
    analysis_service = AnalysisService(db.session)
    
    # 获取关注列表数量
    watchlist_data = stock_service.get_user_watchlist(user_id)
    watchlist_count = watchlist_data['count']
    
    # 获取报告数量
    reports = analysis_service.get_user_reports(user_id, limit=100)
    reports_count = len(reports)
    
    user_data = {
        'email': user_email,
        'watchlist_count': watchlist_count,
        'reports_count': reports_count,
        'plan_type': 'ADMIN' if is_admin else 'TRIAL',
        'remaining_quota': 999 if is_admin else 1,
        'is_admin': is_admin
    }
    return render_template('dashboard/index.html', user=user_data)
