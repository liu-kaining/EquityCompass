"""
分析任务API
"""
from flask import Blueprint
from app.utils.response import success_response

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/trigger', methods=['POST'])
def trigger_analysis():
    """触发分析任务"""
    return success_response(data={'message': '触发分析API'})

@analysis_bp.route('/status', methods=['GET'])
def get_analysis_status():
    """获取任务状态"""
    return success_response(data={'message': '任务状态API'})

@analysis_bp.route('/history', methods=['GET'])
def get_analysis_history():
    """获取分析历史"""
    return success_response(data={'message': '分析历史API'})
