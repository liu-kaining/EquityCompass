"""
统一响应格式工具
"""
from flask import jsonify
from datetime import datetime


def success_response(data=None, message="Success", status_code=200):
    """成功响应格式"""
    response_data = {
        'success': True,
        'data': data,
        'message': message,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    return jsonify(response_data), status_code


def error_response(error_code, message, status_code=400, data=None):
    """错误响应格式"""
    response_data = {
        'success': False,
        'error': error_code,
        'message': message,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    if data:
        response_data['data'] = data
    return jsonify(response_data), status_code


def paginated_response(items, page, per_page, total, data_key='items'):
    """分页响应格式"""
    response_data = {
        'success': True,
        'data': {
            data_key: items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        },
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    return jsonify(response_data), 200


# 服务层响应函数（返回字典，不返回Flask响应对象）
def service_success_response(data=None, message="Success"):
    """服务层成功响应格式（返回字典）"""
    return {
        'success': True,
        'data': data,
        'message': message,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }


def service_error_response(error_code, message, data=None):
    """服务层错误响应格式（返回字典）"""
    response_data = {
        'success': False,
        'error': error_code,
        'message': message,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    if data:
        response_data['data'] = data
    return response_data
