"""
用户相关API
"""
from flask import Blueprint
from app.utils.response import success_response

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    # TODO: 实现获取用户信息逻辑
    return success_response(data={'message': '用户信息API'})

@users_bp.route('/profile', methods=['PUT'])
def update_profile():
    """更新用户信息"""
    # TODO: 实现更新用户信息逻辑
    return success_response(data={'message': '更新用户信息API'})

@users_bp.route('/plan', methods=['GET'])
def get_plan():
    """获取用户计划"""
    # TODO: 实现获取用户计划逻辑
    return success_response(data={'message': '用户计划API'})
