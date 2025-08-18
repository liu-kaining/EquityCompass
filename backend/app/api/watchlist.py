"""
关注列表API
"""
from flask import Blueprint
from app.utils.response import success_response

watchlist_bp = Blueprint('watchlist', __name__)

@watchlist_bp.route('', methods=['GET'])
def get_watchlist():
    """获取关注列表"""
    return success_response(data={'message': '关注列表API'})

@watchlist_bp.route('', methods=['POST'])
def add_to_watchlist():
    """添加到关注列表"""
    return success_response(data={'message': '添加关注API'})

@watchlist_bp.route('/<int:stock_id>', methods=['DELETE'])
def remove_from_watchlist(stock_id):
    """移除关注股票"""
    return success_response(data={'message': f'移除关注API: {stock_id}'})
