"""
主页面视图
"""
from flask import Blueprint, render_template, redirect, url_for, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页"""
    # 如果用户已登录，重定向到仪表板
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    # 否则显示登录页面
    return redirect(url_for('auth.login'))

@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')
