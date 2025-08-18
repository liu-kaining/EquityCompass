"""
支付相关API
"""
from flask import Blueprint
from app.utils.response import success_response

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/plans', methods=['GET'])
def get_payment_plans():
    """获取付费计划"""
    return success_response(data={'message': '付费计划API'})

@payment_bp.route('/create-session', methods=['POST'])
def create_payment_session():
    """创建支付会话"""
    return success_response(data={'message': '支付会话API'})

@payment_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """支付回调"""
    return success_response(data={'message': '支付回调API'})

@payment_bp.route('/history', methods=['GET'])
def get_payment_history():
    """支付历史"""
    return success_response(data={'message': '支付历史API'})
