"""
AI配置管理页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.utils.permissions import super_admin_required, get_user_context
from app.services.ai.ai_config_service import AIConfigService
from app import db
import logging

logger = logging.getLogger(__name__)

ai_config_bp = Blueprint('ai_config', __name__)


@ai_config_bp.route('/ai-configs')
@super_admin_required
def index():
    """AI配置管理页面"""
    try:
        # 获取用户上下文
        user_context = get_user_context()
        
        # 获取AI配置服务
        service = AIConfigService(db.session)
        
        # 获取使用统计
        stats = service.get_usage_stats()
        
        # 获取配置模板
        templates = service.get_provider_templates()
        
        return render_template('admin/ai_configs.html', 
                             user_context=user_context,
                             stats=stats,
                             templates=templates)
        
    except Exception as e:
        logger.error(f"加载AI配置管理页面失败: {str(e)}")
        return redirect(url_for('dashboard.index'))


@ai_config_bp.route('/ai-configs/create')
@super_admin_required
def create_form():
    """AI配置创建表单页面"""
    try:
        # 获取用户上下文
        user_context = get_user_context()
        
        # 获取AI配置服务
        service = AIConfigService(db.session)
        
        # 获取配置模板
        templates = service.get_provider_templates()
        
        return render_template('admin/ai_config_create.html',
                             user_context=user_context,
                             templates=templates)
        
    except Exception as e:
        logger.error(f"加载AI配置创建页面失败: {str(e)}")
        return redirect(url_for('ai_config.index'))


@ai_config_bp.route('/ai-configs/<int:config_id>/edit')
@super_admin_required
def edit_form(config_id):
    """AI配置编辑表单页面"""
    try:
        # 获取用户上下文
        user_context = get_user_context()
        
        # 获取AI配置服务
        service = AIConfigService(db.session)
        
        # 获取配置详情
        config = service.get_config_by_id(config_id, include_sensitive=True)
        if not config:
            return redirect(url_for('ai_config.index'))
        
        # 获取配置模板
        templates = service.get_provider_templates()
        
        return render_template('admin/ai_config_edit.html',
                             user_context=user_context,
                             config=config,
                             templates=templates)
        
    except Exception as e:
        logger.error(f"加载AI配置编辑页面失败: {str(e)}")
        return redirect(url_for('ai_config.index'))
