"""
认证页面视图
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    from flask import make_response
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        # 邮箱格式验证
        if not email:
            flash('请输入邮箱地址', 'error')
            response = make_response(render_template('auth/login.html'))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        
        # 开发阶段：管理员后门登录
        if email == 'admin@dev.com':
            session['user_id'] = 999
            session['user_email'] = email
            session['is_admin'] = True
            session['access_token'] = 'dev_admin_token'
            flash('管理员开发模式登录成功！', 'success')
            return redirect(url_for('dashboard.index'))

        # 开发阶段：普通用户后门登录
        if email == 'user@dev.com':
            session['user_id'] = 1
            session['user_email'] = email
            session['is_admin'] = False
            session['access_token'] = 'dev_user_token'
            flash('开发模式登录成功！', 'success')
            return redirect(url_for('dashboard.index'))

        # 正常流程：使用AJAX发送验证码，这里直接跳转到验证页面
        return redirect(url_for('auth.verify', email=email))

    response = make_response(render_template('auth/login.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    """验证码验证页面"""
    email = request.args.get('email') or request.form.get('email')
    
    if not email:
        flash('请先输入邮箱地址', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        
        if not code:
            flash('请输入验证码', 'error')
            return render_template('auth/verify.html', email=email)
        
        # 这里将使用AJAX与后端API交互
        # 暂时模拟验证成功
        session['user_id'] = 1
        session['user_email'] = email
        session['is_admin'] = False
        flash('登录成功！', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/verify.html', email=email)

@auth_bp.route('/logout')
def logout():
    """登出"""
    from flask import make_response
    
    # 创建响应并设置cookie过期
    response = make_response(redirect(url_for('main.index')))
    response.delete_cookie('session')
    
    # 完全清理session（包括Flash消息）
    session.clear()
    
    return response
