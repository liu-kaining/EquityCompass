"""
提示词管理页面视图
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.utils.permissions import super_admin_required, get_user_context
from app.services.prompt_service import PromptService
from app import db
import logging

logger = logging.getLogger(__name__)

prompt_bp = Blueprint('prompt', __name__)


@prompt_bp.route('/prompts')
@super_admin_required
def index():
    """提示词管理页面"""
    try:
        # 获取用户上下文
        user_context = get_user_context()
        
        # 获取提示词服务
        service = PromptService(db.session)
        
        # 获取使用统计
        stats = service.get_usage_stats()
        
        # 获取提示词类型
        types = service.get_prompt_types()
        
        return render_template('admin/prompts.html', 
                             user_context=user_context,
                             stats=stats,
                             types=types)
        
    except Exception as e:
        logger.error(f"加载提示词管理页面失败: {str(e)}")
        return redirect(url_for('dashboard.index'))


@prompt_bp.route('/prompts/create')
@super_admin_required
def create_form():
    """提示词创建表单页面"""
    try:
        # 获取用户上下文
        user_context = get_user_context()
        
        # 获取提示词服务
        service = PromptService(db.session)
        
        # 获取提示词类型
        types = service.get_prompt_types()
        
        return render_template('admin/prompt_create.html',
                             user_context=user_context,
                             types=types)
        
    except Exception as e:
        logger.error(f"加载提示词创建页面失败: {str(e)}")
        return redirect(url_for('prompt.index'))


@prompt_bp.route('/prompts/<int:prompt_id>/edit')
@super_admin_required
def edit_form(prompt_id):
    """提示词编辑表单页面"""
    try:
        # 获取用户上下文
        user_context = get_user_context()
        
        # 获取提示词服务
        service = PromptService(db.session)
        
        # 获取提示词详情
        prompt_dict = service.get_prompt_by_id(prompt_id)
        if not prompt_dict:
            return redirect(url_for('prompt.index'))
        
        # 获取提示词对象
        from app.repositories.prompt_repository import PromptRepository
        prompt_repo = PromptRepository(db.session)
        prompt = prompt_repo.get_by_id(prompt_id)
        if not prompt:
            return redirect(url_for('prompt.index'))
        
        # 获取提示词类型
        types = service.get_prompt_types()
        
        return render_template('admin/prompt_edit.html',
                             user_context=user_context,
                             prompt=prompt,
                             types=types)
        
    except Exception as e:
        logger.error(f"加载提示词编辑页面失败: {str(e)}")
        return redirect(url_for('prompt.index'))


@prompt_bp.route('/prompts/<name>/versions')
@super_admin_required
def versions(name):
    """提示词版本管理页面"""
    try:
        # 获取用户上下文
        user_context = get_user_context()
        
        # 获取提示词服务
        service = PromptService(db.session)
        
        # 获取提示词的所有版本
        versions_dict = service.get_prompt_versions(name)
        if not versions_dict:
            return redirect(url_for('prompt.index'))
        
        # 获取版本对象
        from app.repositories.prompt_repository import PromptRepository
        prompt_repo = PromptRepository(db.session)
        versions = prompt_repo.get_by_name(name)
        
        return render_template('admin/prompt_versions.html',
                             user_context=user_context,
                             prompt_name=name,
                             versions=versions)
        
    except Exception as e:
        logger.error(f"加载提示词版本页面失败: {str(e)}")
        return redirect(url_for('prompt.index'))
