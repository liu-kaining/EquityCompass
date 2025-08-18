"""
系统监控API
"""
from flask import Blueprint
from app.utils.response import success_response
from app import db, redis_client
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
    
    try:
        # Redis连接检查
        redis_client.ping()
        redis_status = 'healthy'
    except Exception:
        redis_status = 'unhealthy'
    
    # TODO: Celery检查
    celery_status = 'healthy'
    
    overall_status = 'healthy' if all([
        db_status == 'healthy',
        redis_status == 'healthy',
        celery_status == 'healthy'
    ]) else 'unhealthy'
    
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
