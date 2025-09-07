"""
提示词管理API
"""
from flask import Blueprint, request, jsonify, session
from app import db
from app.services.prompt_service import PromptService
from app.utils.permissions import login_required, super_admin_required
from app.utils.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)

prompt_api_bp = Blueprint('prompt_api', __name__)


def get_prompt_service():
    """获取提示词服务实例"""
    return PromptService(db.session)


@prompt_api_bp.route('/prompts', methods=['GET'])
@super_admin_required
def get_all_prompts():
    """获取所有提示词"""
    try:
        service = get_prompt_service()
        prompts = service.get_all_prompts()
        
        return success_response(data={
            'prompts': prompts,
            'count': len(prompts)
        })
        
    except Exception as e:
        logger.error(f"获取提示词失败: {str(e)}")
        return error_response("获取提示词失败", str(e))


@prompt_api_bp.route('/prompts/<int:prompt_id>', methods=['GET'])
@super_admin_required
def get_prompt(prompt_id):
    """获取指定提示词"""
    try:
        service = get_prompt_service()
        prompt = service.get_prompt_by_id(prompt_id)
        
        if not prompt:
            return error_response("提示词不存在", "NOT_FOUND")
        
        return success_response(data=prompt)
        
    except Exception as e:
        logger.error(f"获取提示词失败: {str(e)}")
        return error_response("获取提示词失败", str(e))


@prompt_api_bp.route('/prompts', methods=['POST'])
@super_admin_required
def create_prompt():
    """创建新的提示词"""
    try:
        data = request.get_json()
        if not data:
            return error_response("INVALID_PARAM", "请求数据不能为空")
        
        # 添加创建者信息
        data['created_by'] = session.get('user_id')
        
        service = get_prompt_service()
        result = service.create_prompt(data)
        
        if result['success']:
            return success_response(
                data=result['data'],
                message=result['message']
            )
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"创建提示词失败: {str(e)}")
        return error_response("创建提示词失败", str(e))


@prompt_api_bp.route('/prompts/<int:prompt_id>', methods=['PUT'])
@super_admin_required
def update_prompt(prompt_id):
    """更新提示词"""
    try:
        data = request.get_json()
        if not data:
            return error_response("INVALID_PARAM", "请求数据不能为空")
        
        service = get_prompt_service()
        result = service.update_prompt(prompt_id, data)
        
        if result['success']:
            return success_response(
                data=result['data'],
                message=result['message']
            )
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"更新提示词失败: {str(e)}")
        return error_response("更新提示词失败", str(e))


@prompt_api_bp.route('/prompts/<int:prompt_id>', methods=['DELETE'])
@super_admin_required
def delete_prompt(prompt_id):
    """删除提示词"""
    try:
        service = get_prompt_service()
        result = service.delete_prompt(prompt_id)
        
        if result['success']:
            return success_response(message=result['message'])
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"删除提示词失败: {str(e)}")
        return error_response("删除提示词失败", str(e))


@prompt_api_bp.route('/prompts/<int:prompt_id>/toggle-active', methods=['POST'])
@super_admin_required
def toggle_prompt_active(prompt_id):
    """切换提示词激活状态"""
    try:
        service = get_prompt_service()
        result = service.toggle_active(prompt_id)
        
        if result['success']:
            return success_response(
                data=result['data'],
                message=result['message']
            )
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"切换提示词状态失败: {str(e)}")
        return error_response("操作失败", str(e))


@prompt_api_bp.route('/prompts/<int:prompt_id>/set-default', methods=['POST'])
@super_admin_required
def set_default_prompt(prompt_id):
    """设置默认提示词"""
    try:
        service = get_prompt_service()
        result = service.set_default_version(prompt_id)
        
        if result['success']:
            return success_response(message=result['message'])
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"设置默认提示词失败: {str(e)}")
        return error_response("操作失败", str(e))


@prompt_api_bp.route('/prompts/<int:prompt_id>/new-version', methods=['POST'])
@super_admin_required
def create_new_version(prompt_id):
    """创建新版本"""
    try:
        data = request.get_json()
        if not data:
            return error_response("INVALID_PARAM", "请求数据不能为空")
        
        # 获取原提示词信息
        service = get_prompt_service()
        original_prompt = service.get_prompt_by_id(prompt_id)
        if not original_prompt:
            return error_response("NOT_FOUND", "原提示词不存在")
        
        # 创建新版本
        result = service.create_new_version(
            name=original_prompt['name'],
            prompt_type=original_prompt['prompt_type'],
            content=data.get('content', original_prompt['content']),
            description=data.get('description', original_prompt['description']),
            created_by=session.get('user_id')
        )
        
        if result['success']:
            return success_response(
                data=result['data'],
                message=result['message']
            )
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"创建新版本失败: {str(e)}")
        return error_response("创建新版本失败", str(e))


@prompt_api_bp.route('/prompts/type/<prompt_type>', methods=['GET'])
@login_required
def get_prompts_by_type(prompt_type):
    """根据类型获取提示词（普通用户可访问）"""
    try:
        service = get_prompt_service()
        prompts = service.get_prompts_by_type(prompt_type)
        
        return success_response(data={
            'prompts': prompts,
            'count': len(prompts)
        })
        
    except Exception as e:
        logger.error(f"获取提示词失败: {str(e)}")
        return error_response("获取提示词失败", str(e))


@prompt_api_bp.route('/prompts/type/<prompt_type>/default', methods=['GET'])
@login_required
def get_default_prompt(prompt_type):
    """获取默认提示词（普通用户可访问）"""
    try:
        service = get_prompt_service()
        prompt = service.get_default_prompt(prompt_type)
        
        if not prompt:
            return error_response("没有默认提示词", "NOT_FOUND")
        
        return success_response(data=prompt)
        
    except Exception as e:
        logger.error(f"获取默认提示词失败: {str(e)}")
        return error_response("获取提示词失败", str(e))


@prompt_api_bp.route('/prompts/name/<name>', methods=['GET'])
@super_admin_required
def get_prompt_versions(name):
    """获取提示词的所有版本"""
    try:
        service = get_prompt_service()
        prompts = service.get_prompt_versions(name)
        
        return success_response(data={
            'versions': prompts,
            'count': len(prompts)
        })
        
    except Exception as e:
        logger.error(f"获取提示词版本失败: {str(e)}")
        return error_response("获取提示词版本失败", str(e))


@prompt_api_bp.route('/prompts/stats', methods=['GET'])
@super_admin_required
def get_usage_stats():
    """获取使用统计"""
    try:
        service = get_prompt_service()
        stats = service.get_usage_stats()
        
        return success_response(data=stats)
        
    except Exception as e:
        logger.error(f"获取使用统计失败: {str(e)}")
        return error_response("获取统计失败", str(e))


@prompt_api_bp.route('/prompts/search', methods=['GET'])
@super_admin_required
def search_prompts():
    """搜索提示词"""
    try:
        query = request.args.get('q', '')
        if not query:
            return error_response("INVALID_PARAM", "搜索关键词不能为空")
        
        service = get_prompt_service()
        prompts = service.search_prompts(query)
        
        return success_response(data={
            'prompts': prompts,
            'count': len(prompts),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"搜索提示词失败: {str(e)}")
        return error_response("搜索失败", str(e))


@prompt_api_bp.route('/prompts/import-default', methods=['POST'])
@super_admin_required
def import_default_prompts():
    """导入默认提示词"""
    try:
        service = get_prompt_service()
        result = service.import_default_prompts()
        
        if result['success']:
            return success_response(
                data={'imported_count': result['imported_count']},
                message=result['message']
            )
        else:
            return error_response(result['error'])
            
    except Exception as e:
        logger.error(f"导入默认提示词失败: {str(e)}")
        return error_response("导入失败", str(e))


@prompt_api_bp.route('/prompts/types', methods=['GET'])
@super_admin_required
def get_prompt_types():
    """获取所有提示词类型"""
    try:
        service = get_prompt_service()
        types = service.get_prompt_types()
        
        return success_response(data=types)
        
    except Exception as e:
        logger.error(f"获取提示词类型失败: {str(e)}")
        return error_response("获取类型失败", str(e))
