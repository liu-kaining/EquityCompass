"""
系统监控API
"""
from flask import Blueprint
from app.utils.response import success_response
from app import db
import time

health_bp = Blueprint('health', __name__)

@health_bp.route('', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        # 数据库连接检查
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception:
        db_status = 'unhealthy'
    
    # Redis状态（已移除依赖）
    redis_status = 'not_configured'
    
    # Celery状态（已移除依赖）
    celery_status = 'not_configured'
    
    overall_status = 'healthy' if db_status == 'healthy' else 'unhealthy'
    
    return success_response(data={
        'status': overall_status,
        'timestamp': time.time(),
        'services': {
            'database': db_status,
            'redis': redis_status,
            'celery': celery_status
        }
    })

@health_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """系统指标"""
    # TODO: 实现系统指标收集
    return success_response(data={'message': '系统指标API'})
