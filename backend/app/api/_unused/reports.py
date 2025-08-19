"""
报告相关API
"""
from flask import Blueprint
from app.utils.response import success_response

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('', methods=['GET'])
def get_reports():
    """获取报告列表"""
    return success_response(data={'message': '报告列表API'})

@reports_bp.route('/<int:report_id>', methods=['GET'])
def get_report_detail(report_id):
    """获取报告详情"""
    return success_response(data={'message': f'报告详情API: {report_id}'})

@reports_bp.route('/search', methods=['GET'])
def search_reports():
    """搜索报告"""
    return success_response(data={'message': '搜索报告API'})

@reports_bp.route('/export', methods=['POST'])
def export_reports():
    """导出报告"""
    return success_response(data={'message': '导出报告API'})
