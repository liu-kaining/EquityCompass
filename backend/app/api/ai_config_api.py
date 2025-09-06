"""
AI配置管理API
"""
from flask import Blueprint, request, jsonify, session
from app import db
from app.services.ai.ai_config_service import AIConfigService
from app.utils.permissions import login_required, super_admin_required
from app.utils.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)

ai_config_api_bp = Blueprint('ai_config_api', __name__)


def get_ai_config_service():
    """获取AI配置服务实例"""
    return AIConfigService(db.session)


@ai_config_api_bp.route('/configs', methods=['GET'])
@super_admin_required
def get_all_configs():
    """获取所有AI配置"""
    try:
        service = get_ai_config_service()
        include_sensitive = request.args.get('include_sensitive', 'false').lower() == 'true'
        configs = service.get_all_configs(include_sensitive=include_sensitive)
        
        return success_response(data={
            'configs': configs,
            'count': len(configs)
        })
        
    except Exception as e:
        logger.error(f"获取AI配置失败: {str(e)}")
        return error_response("获取配置失败", str(e))


@ai_config_api_bp.route('/configs/<int:config_id>', methods=['GET'])
@super_admin_required
def get_config(config_id):
    """获取指定AI配置"""
    try:
        service = get_ai_config_service()
        include_sensitive = request.args.get('include_sensitive', 'false').lower() == 'true'
        config = service.get_config_by_id(config_id, include_sensitive=include_sensitive)
        
        if not config:
            return error_response("配置不存在", "NOT_FOUND")
        
        return success_response(data=config)
        
    except Exception as e:
        logger.error(f"获取AI配置失败: {str(e)}")
        return error_response("获取配置失败", str(e))


@ai_config_api_bp.route('/configs', methods=['POST'])
@super_admin_required
def create_config():
    """创建新的AI配置"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空")
        
        # 添加创建者信息
        data['created_by'] = session.get('user_id')
        
        service = get_ai_config_service()
        result = service.create_config(data)
        
        if result['success']:
            return success_response(
                data=result['data'],
                message=result['message']
            )
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"创建AI配置失败: {str(e)}")
        return error_response("创建配置失败", str(e))


@ai_config_api_bp.route('/configs/<int:config_id>', methods=['PUT'])
@super_admin_required
def update_config(config_id):
    """更新AI配置"""
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空")
        
        service = get_ai_config_service()
        result = service.update_config(config_id, data)
        
        if result['success']:
            return success_response(
                data=result['data'],
                message=result['message']
            )
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"更新AI配置失败: {str(e)}")
        return error_response("更新配置失败", str(e))


@ai_config_api_bp.route('/configs/<int:config_id>', methods=['DELETE'])
@super_admin_required
def delete_config(config_id):
    """删除AI配置"""
    try:
        service = get_ai_config_service()
        result = service.delete_config(config_id)
        
        if result['success']:
            return success_response(message=result['message'])
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"删除AI配置失败: {str(e)}")
        return error_response("删除配置失败", str(e))


@ai_config_api_bp.route('/configs/<int:config_id>/toggle-active', methods=['POST'])
@super_admin_required
def toggle_config_active(config_id):
    """切换配置激活状态"""
    try:
        service = get_ai_config_service()
        result = service.toggle_active(config_id)
        
        if result['success']:
            return success_response(
                data=result['data'],
                message=result['message']
            )
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"切换配置状态失败: {str(e)}")
        return error_response("操作失败", str(e))


@ai_config_api_bp.route('/configs/<int:config_id>/set-default', methods=['POST'])
@super_admin_required
def set_default_config(config_id):
    """设置默认配置"""
    try:
        service = get_ai_config_service()
        result = service.set_default_config(config_id)
        
        if result['success']:
            return success_response(message=result['message'])
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"设置默认配置失败: {str(e)}")
        return error_response("操作失败", str(e))


@ai_config_api_bp.route('/configs/<int:config_id>/test', methods=['POST'])
@super_admin_required
def test_config(config_id):
    """测试配置连接"""
    try:
        service = get_ai_config_service()
        result = service.test_config(config_id)
        
        if result['success']:
            return success_response(
                data=result,
                message=result['message']
            )
        else:
            return error_response(result.get('error', '测试失败'))
            
    except Exception as e:
        logger.error(f"测试配置失败: {str(e)}")
        return error_response("测试失败", str(e))


@ai_config_api_bp.route('/configs/active', methods=['GET'])
@login_required
def get_active_configs():
    """获取激活的配置（普通用户可访问）"""
    try:
        service = get_ai_config_service()
        configs = service.get_active_configs()
        
        return success_response(data={
            'configs': configs,
            'count': len(configs)
        })
        
    except Exception as e:
        logger.error(f"获取激活配置失败: {str(e)}")
        return error_response("获取配置失败", str(e))


@ai_config_api_bp.route('/configs/default', methods=['GET'])
@login_required
def get_default_config():
    """获取默认配置（普通用户可访问）"""
    try:
        service = get_ai_config_service()
        config = service.get_default_config()
        
        if not config:
            return error_response("没有默认配置", "NOT_FOUND")
        
        return success_response(data=config)
        
    except Exception as e:
        logger.error(f"获取默认配置失败: {str(e)}")
        return error_response("获取配置失败", str(e))


@ai_config_api_bp.route('/configs/stats', methods=['GET'])
@super_admin_required
def get_usage_stats():
    """获取使用统计"""
    try:
        service = get_ai_config_service()
        stats = service.get_usage_stats()
        
        return success_response(data=stats)
        
    except Exception as e:
        logger.error(f"获取使用统计失败: {str(e)}")
        return error_response("获取统计失败", str(e))


@ai_config_api_bp.route('/configs/templates', methods=['GET'])
@super_admin_required
def get_provider_templates():
    """获取提供商配置模板"""
    try:
        service = get_ai_config_service()
        templates = service.get_provider_templates()
        
        return success_response(data=templates)
        
    except Exception as e:
        logger.error(f"获取配置模板失败: {str(e)}")
        return error_response("获取模板失败", str(e))


@ai_config_api_bp.route('/configs/import-env', methods=['POST'])
@super_admin_required
def import_from_env():
    """从环境变量导入配置"""
    try:
        service = get_ai_config_service()
        result = service.import_from_env()
        
        if result['success']:
            return success_response(
                data={'imported_count': result['imported_count']},
                message=result['message']
            )
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"从环境变量导入配置失败: {str(e)}")
        return error_response("导入失败", str(e))
