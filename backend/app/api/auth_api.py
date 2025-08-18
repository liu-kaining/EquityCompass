"""
认证相关API
"""
from flask import Blueprint, request, jsonify
from app.utils.response import success_response, error_response

auth_api_bp = Blueprint('auth_api', __name__)

@auth_api_bp.route('/send-code', methods=['POST'])
def send_verification_code():
    """发送验证码"""
    # TODO: 实现发送验证码逻辑
    return success_response(data={'message': '验证码已发送'})

@auth_api_bp.route('/verify-code', methods=['POST'])
def verify_code():
    """验证登录"""
    # TODO: 实现验证码验证逻辑
    return success_response(data={'token': 'mock_token'})

@auth_api_bp.route('/logout', methods=['POST'])
def logout():
    """登出"""
    # TODO: 实现登出逻辑
    return success_response(data={'message': '登出成功'})

@auth_api_bp.route('/status', methods=['GET'])
def status():
    """检查登录状态"""
    # TODO: 实现状态检查逻辑
    return success_response(data={'authenticated': False})
