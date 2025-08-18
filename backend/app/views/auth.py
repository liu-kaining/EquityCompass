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
        # TODO: 实现邮箱验证码登录逻辑
        flash('验证码已发送到您的邮箱', 'info')
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
