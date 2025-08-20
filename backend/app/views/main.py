"""
主页面视图
"""
from flask import Blueprint, render_template, redirect, url_for, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页"""
    from flask import make_response
    
    # 如果用户已登录，重定向到仪表板
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    
    # 否则显示首页介绍
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')
