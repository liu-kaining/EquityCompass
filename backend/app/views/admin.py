"""
管理员页面视图
"""
from flask import Blueprint, render_template, request, jsonify, session
from app.utils.permissions import (
    login_required, super_admin_required, user_management_required,
    get_user_context
)
from app.repositories.user_repository import UserRepository
from app import db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users')
@user_management_required
def user_management():
    """用户管理页面（仅超级管理员）"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 获取用户数据
        user_repo = UserRepository(db.session)
        users = user_repo.get_all_users(page, per_page)
        user_stats = user_repo.get_user_stats()
        
        # 格式化用户数据
        formatted_users = []
        for user in users:
            formatted_users.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nickname': user.nickname,
                'user_role': user.user_role,
                'plan_type': user.plan_type,
                'remaining_quota': user.remaining_quota,
                'is_active': user.is_active,
                'email_verified': user.email_verified,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        # 构建分页信息
        total_users = user_stats['total_users']
        total_pages = (total_users + per_page - 1) // per_page
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total_users,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }
        
        return render_template('admin/users.html', 
                             users=formatted_users, 
                             user_stats=user_stats,
                             pagination=pagination)
        
    except Exception as e:
        return render_template('admin/users.html', 
                             users=[], 
                             user_stats={},
                             pagination=None,
                             error=str(e))


@admin_bp.route('/api/users/<int:user_id>/role', methods=['PUT'])
@user_management_required
def update_user_role(user_id):
    """更新用户角色"""
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['SUPER_ADMIN', 'SITE_ADMIN', 'USER']:
            return jsonify({
                'success': False,
                'error': 'INVALID_ROLE',
                'message': '无效的用户角色'
            }), 400
        
        user_repo = UserRepository(db.session)
        user = user_repo.update_user_role(user_id, new_role)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'USER_NOT_FOUND',
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '用户角色更新成功',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'user_role': user.user_role
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'UPDATE_FAILED',
            'message': f'更新失败: {str(e)}'
        }), 500


@admin_bp.route('/api/users/<int:user_id>/status', methods=['PUT'])
@user_management_required
def update_user_status(user_id):
    """更新用户状态（启用/禁用）"""
    try:
        data = request.get_json()
        is_active = data.get('is_active')
        
        if not isinstance(is_active, bool):
            return jsonify({
                'success': False,
                'error': 'INVALID_STATUS',
                'message': '无效的状态值'
            }), 400
        
        user_repo = UserRepository(db.session)
        
        if is_active:
            user = user_repo.activate_user(user_id)
        else:
            user = user_repo.deactivate_user(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'USER_NOT_FOUND',
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': f'用户已{"启用" if is_active else "禁用"}',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'is_active': user.is_active
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'UPDATE_FAILED',
            'message': f'更新失败: {str(e)}'
        }), 500


@admin_bp.route('/api/users/<int:user_id>/details')
@user_management_required
def get_user_details(user_id):
    """获取用户详细信息"""
    try:
        user_repo = UserRepository(db.session)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'USER_NOT_FOUND',
                'message': '用户不存在'
            }), 404
        
        # 获取用户的关注列表
        from app.services.data.stock_service import StockDataService
        stock_service = StockDataService(db.session)
        watchlist_data = stock_service.get_user_watchlist(user_id)
        
        # 获取用户的报告
        from app.services.ai.analysis_service import AnalysisService
        analysis_service = AnalysisService(db.session)
        user_reports = analysis_service.get_user_reports(user_id, limit=50)
        
        # 获取用户的任务
        user_tasks = analysis_service.get_user_tasks(user_id, limit=50)
        
        return jsonify({
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'nickname': user.nickname,
                    'user_role': user.user_role,
                    'plan_type': user.plan_type,
                    'remaining_quota': user.remaining_quota,
                    'is_active': user.is_active,
                    'email_verified': user.email_verified,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                },
                'watchlist': {
                    'count': watchlist_data['count'],
                    'stocks': watchlist_data['watchlist']
                },
                'reports': {
                    'count': len(user_reports),
                    'reports': user_reports[:10]  # 只返回前10个报告
                },
                'tasks': {
                    'count': len(user_tasks),
                    'tasks': user_tasks[:10]  # 只返回前10个任务
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'FETCH_FAILED',
            'message': f'获取用户详情失败: {str(e)}'
        }), 500
