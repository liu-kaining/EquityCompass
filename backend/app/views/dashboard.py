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
    # 获取用户数据
    user_email = session.get('user_email', '')
    is_admin = session.get('is_admin', False)
    
    user_data = {
        'email': user_email,
        'watchlist_count': 5 if not is_admin else 15,  # 模拟数据
        'reports_count': 3 if not is_admin else 8,     # 模拟数据
        'plan_type': 'ADMIN' if is_admin else 'TRIAL',
        'remaining_quota': 999 if is_admin else 1,
        'is_admin': is_admin
    }
    return render_template('dashboard/index.html', user=user_data)
