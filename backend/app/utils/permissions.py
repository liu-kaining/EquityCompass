"""
权限控制工具
"""
from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from app.repositories.user_repository import UserRepository
from app import db


def get_current_user():
    """获取当前登录用户"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    user_repo = UserRepository(db.session)
    return user_repo.get_by_id(user_id)


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'LOGIN_REQUIRED',
                    'message': '请先登录'
                }), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员权限装饰器（超级管理员或网站管理员）"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin():
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'ADMIN_REQUIRED',
                    'message': '需要管理员权限'
                }), 403
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def super_admin_required(f):
    """超级管理员权限装饰器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_super_admin():
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'SUPER_ADMIN_REQUIRED',
                    'message': '需要超级管理员权限'
                }), 403
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def site_admin_required(f):
    """网站管理员权限装饰器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_site_admin():
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'SITE_ADMIN_REQUIRED',
                    'message': '需要网站管理员权限'
                }), 403
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def user_management_required(f):
    """用户管理权限装饰器（仅超级管理员）"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.can_manage_users():
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'USER_MANAGEMENT_REQUIRED',
                    'message': '需要用户管理权限'
                }), 403
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def statistics_access_required(f):
    """统计页面访问权限装饰器（管理员）"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.can_view_statistics():
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'STATISTICS_ACCESS_REQUIRED',
                    'message': '需要统计页面访问权限'
                }), 403
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def check_report_download_permission(report_user_id):
    """检查报告下载权限"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    # 管理员可以下载所有报告
    if current_user.can_download_all_reports():
        return True
    
    # 普通用户只能下载自己的报告
    return current_user.id == report_user_id


def check_report_view_permission(report_user_id):
    """检查报告查看权限"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    # 管理员可以查看所有报告
    if current_user.can_view_all_reports():
        return True
    
    # 普通用户可以查看所有报告（但不能下载别人的）
    return True


def require_permission(permission):
    """权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'LOGIN_REQUIRED',
                        'message': '请先登录'
                    }), 401
                return redirect(url_for('auth.login'))
            
            # 检查权限
            if permission == 'SUPER_ADMIN' and not user.is_super_admin():
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'SUPER_ADMIN_REQUIRED',
                        'message': '需要超级管理员权限'
                    }), 403
                return redirect(url_for('dashboard.index'))
            
            if permission == 'SITE_ADMIN' and not user.is_site_admin():
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'SITE_ADMIN_REQUIRED',
                        'message': '需要网站管理员权限'
                    }), 403
                return redirect(url_for('dashboard.index'))
            
            if permission == 'ADMIN' and not user.is_admin():
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': 'ADMIN_REQUIRED',
                        'message': '需要管理员权限'
                    }), 403
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_user_context():
    """获取用户上下文信息"""
    user = get_current_user()
    if not user:
        return None
    
    return {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'nickname': user.nickname,
        'user_role': user.user_role,
        'is_super_admin': user.is_super_admin(),
        'is_site_admin': user.is_site_admin(),
        'is_admin': user.is_admin(),
        'can_manage_users': user.can_manage_users(),
        'can_view_all_reports': user.can_view_all_reports(),
        'can_download_all_reports': user.can_download_all_reports(),
        'can_view_statistics': user.can_view_statistics()
    }
