"""
报告页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for

reports_bp = Blueprint('reports', __name__)

def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@reports_bp.route('/')
@login_required
def index():
    """报告列表页面"""
    # TODO: 获取报告数据
    reports_data = []
    return render_template('reports/index.html', reports=reports_data)

@reports_bp.route('/<int:report_id>')
@login_required
def detail(report_id):
    """报告详情页面"""
    # TODO: 获取报告详情
    report_data = {'id': report_id, 'content': '报告内容'}
    return render_template('reports/detail.html', report=report_data)
