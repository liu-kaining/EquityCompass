"""
分析页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for

analysis_bp = Blueprint('analysis', __name__)

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@analysis_bp.route('/')
@login_required
def index():
    """分析任务页面"""
    # TODO: 获取分析任务数据
    tasks_data = []
    return render_template('analysis/index.html', tasks=tasks_data)
