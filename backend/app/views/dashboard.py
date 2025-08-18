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
    # TODO: 获取用户数据
    user_data = {
        'email': session.get('user_email', ''),
        'watchlist_count': 0,
        'reports_count': 0,
        'plan_type': 'TRIAL',
        'remaining_quota': 1
    }
    return render_template('dashboard/index.html', user=user_data)
