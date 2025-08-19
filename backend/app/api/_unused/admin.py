"""
管理员API
"""
from flask import Blueprint
from app.utils.response import success_response

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    return success_response(data={'message': '管理员登录API'})

@admin_bp.route('/users', methods=['GET'])
def admin_get_users():
    """用户管理"""
    return success_response(data={'message': '用户管理API'})

@admin_bp.route('/stocks', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_manage_stocks():
    """股票池管理"""
    return success_response(data={'message': '股票池管理API'})

@admin_bp.route('/prompts', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_manage_prompts():
    """Prompt管理"""
    return success_response(data={'message': 'Prompt管理API'})

@admin_bp.route('/tasks', methods=['GET'])
def admin_get_tasks():
    """任务监控"""
    return success_response(data={'message': '任务监控API'})
