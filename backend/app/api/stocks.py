"""
股票池API
"""
from flask import Blueprint
from app.utils.response import success_response

stocks_bp = Blueprint('stocks', __name__)

@stocks_bp.route('', methods=['GET'])
def get_stocks():
    """获取股票列表"""
    return success_response(data={'message': '股票列表API'})

@stocks_bp.route('/search', methods=['GET'])
def search_stocks():
    """搜索股票"""
    return success_response(data={'message': '搜索股票API'})

@stocks_bp.route('', methods=['POST'])
def add_stock():
    """添加自定义股票"""
    return success_response(data={'message': '添加股票API'})

@stocks_bp.route('/builtin', methods=['GET'])
def get_builtin_stocks():
    """获取内置股票池"""
    return success_response(data={'message': '内置股票池API'})
