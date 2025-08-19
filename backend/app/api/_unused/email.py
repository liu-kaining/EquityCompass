"""
邮件订阅API
"""
from flask import Blueprint
from app.utils.response import success_response

email_bp = Blueprint('email', __name__)

@email_bp.route('/settings', methods=['GET'])
def get_email_settings():
    """获取邮件设置"""
    return success_response(data={'message': '邮件设置API'})

@email_bp.route('/settings', methods=['PUT'])
def update_email_settings():
    """更新邮件设置"""
    return success_response(data={'message': '更新邮件设置API'})

@email_bp.route('/unsubscribe', methods=['POST'])
def unsubscribe_email():
    """取消订阅"""
    return success_response(data={'message': '取消订阅API'})
