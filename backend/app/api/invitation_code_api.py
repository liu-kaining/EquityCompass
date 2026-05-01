"""
邀请码管理API（管理员）
"""
from flask import Blueprint, request, jsonify, session
from sqlalchemy.orm import sessionmaker

from app.services.invitation_code_service import InvitationCodeService
from app.utils.permissions import super_admin_required
from app.utils.response import success_response, error_response

# 创建蓝图
invitation_code_bp = Blueprint('invitation_code_api', __name__)

# 数据库会话
def get_db_session():
    from app import db
    return db.session

def login_required(f):
    """登录验证装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify(error_response("LOGIN_REQUIRED", "请先登录")), 401
        return f(*args, **kwargs)
    return decorated_function


@invitation_code_bp.route('/generate', methods=['POST'])
@login_required
@super_admin_required
def generate_invitation_codes():
    """生成邀请码（单个或批量，仅超级管理员）"""
    try:
        data = request.get_json()
        if not data:
            return error_response("INVALID_REQUEST", "请求数据格式错误")
        
        count = data.get('count', 1)
        
        # 验证数量
        try:
            count = int(count)
            if count < 1:
                return error_response("INVALID_COUNT", "生成数量必须大于0")
            if count > 10:
                return error_response("INVALID_COUNT", "批量生成数量不能超过10个")
        except (ValueError, TypeError):
            return error_response("INVALID_COUNT", "生成数量格式错误")
        
        db_session = get_db_session()
        invitation_service = InvitationCodeService(db_session)
        
        admin_id = session.get('user_id')
        
        # 根据数量选择生成方式
        if count == 1:
            result = invitation_service.generate_code(created_by=admin_id, code_type='INVITATION')
        else:
            result = invitation_service.generate_codes_batch(created_by=admin_id, count=count, code_type='INVITATION')
        
        return result
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"生成邀请码失败: {str(e)}")
        return error_response("GENERATION_FAILED", "生成邀请码失败")


@invitation_code_bp.route('/list', methods=['GET'])
@login_required
@super_admin_required
def get_invitation_codes():
    """获取邀请码列表（仅超级管理员）"""
    try:
        status = request.args.get('status', 'all')  # all/used/unused
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 验证参数
        if status not in ['all', 'used', 'unused']:
            status = 'all'
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        db_session = get_db_session()
        invitation_service = InvitationCodeService(db_session)
        
        result = invitation_service.get_code_list(
            code_type='INVITATION',
            status=status,
            page=page,
            per_page=per_page
        )
        
        return result
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"获取邀请码列表失败: {str(e)}")
        return error_response("GET_LIST_FAILED", "获取邀请码列表失败")


@invitation_code_bp.route('/<int:code_id>', methods=['GET'])
@login_required
@super_admin_required
def get_invitation_code_detail(code_id):
    """获取邀请码详情（仅超级管理员）"""
    try:
        db_session = get_db_session()
        invitation_service = InvitationCodeService(db_session)
        
        result = invitation_service.get_code_detail(code_id)
        return result
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"获取邀请码详情失败: {str(e)}")
        return error_response("GET_DETAIL_FAILED", "获取邀请码详情失败")


@invitation_code_bp.route('/statistics', methods=['GET'])
@login_required
@super_admin_required
def get_statistics():
    """获取邀请码统计信息（仅超级管理员）"""
    try:
        db_session = get_db_session()
        invitation_service = InvitationCodeService(db_session)
        
        result = invitation_service.get_statistics(code_type='INVITATION')
        return result
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"获取统计信息失败: {str(e)}")
        return error_response("GET_STATS_FAILED", "获取统计信息失败")


@invitation_code_bp.route('/export/unused', methods=['GET'])
@login_required
@super_admin_required
def export_unused_codes():
    """导出未使用的邀请码列表（CSV格式，仅超级管理员）"""
    try:
        db_session = get_db_session()
        invitation_service = InvitationCodeService(db_session)
        
        result = invitation_service.export_unused_codes(code_type='INVITATION')
        
        if not result['success']:
            return result
        
        # 生成CSV内容
        import csv
        import io
        from flask import Response
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # CSV头部
        writer.writerow(['邀请码', '格式化显示', '创建时间', '创建者'])
        
        # CSV数据
        for code_data in result['data']['codes']:
            writer.writerow([
                code_data['code'],
                code_data['code_display'],
                code_data['created_at'],
                code_data['creator']
            ])
        
        from datetime import datetime
        # 创建响应
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=invitation_codes_unused_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
        
        return response
        
    except Exception as e:
        from flask import current_app
        from datetime import datetime
        current_app.logger.error(f"导出邀请码失败: {str(e)}")
        return error_response("EXPORT_FAILED", "导出邀请码失败")

