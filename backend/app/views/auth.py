"""
认证页面视图
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        # 开发阶段：管理员后门登录
        if email == 'admin@dev.com':
            session['user_id'] = 999
            session['user_email'] = email
            session['is_admin'] = True
            flash('管理员开发模式登录成功！', 'success')
            return redirect(url_for('dashboard.index'))
        
        # 开发阶段：普通用户后门登录
        if email == 'user@dev.com':
            session['user_id'] = 1
            session['user_email'] = email
            session['is_admin'] = False
            flash('开发模式登录成功！', 'success')
            return redirect(url_for('dashboard.index'))
        
        # 正常流程：发送验证码（暂时跳过实际发送）
        flash('验证码已发送到您的邮箱（开发阶段暂未实现邮件发送）', 'info')
        return render_template('auth/verify.html', email=email)
    
    return render_template('auth/login.html')

@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    """验证码验证页面"""
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        # TODO: 实现验证码验证逻辑
        
        # 模拟登录成功
        session['user_id'] = 1
        session['user_email'] = email
        flash('登录成功！', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/verify.html')

@auth_bp.route('/logout')
def logout():
    """登出"""
    session.clear()
    flash('您已成功登出', 'info')
    return redirect(url_for('auth.login'))
