"""
用户认证API
"""
import re
from flask import Blueprint, request, jsonify, current_app
from app.services.auth.verification_code_service import VerificationCodeService
from app.services.auth.jwt_service import JWTService, jwt_required
from app.services.email.email_service import EmailService
from app.services.data.user_service import UserDataService
from app.repositories.user_repository import UserRepository
from app.utils.validation import UserValidator
from app import db
from datetime import datetime

auth_api_bp = Blueprint('auth_api', __name__)


def is_valid_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@auth_api_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': '请求数据格式错误'
            }), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        nickname = data.get('nickname', '').strip()
        
        # 验证注册数据
        validation_result = UserValidator.validate_registration_data(
            username, email, password, confirm_password
        )
        
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': validation_result['error'],
                'message': validation_result['message']
            }), 400
        
        # 检查用户名和邮箱是否已存在
        user_repo = UserRepository(db.session)
        
        if user_repo.get_by_username(username):
            return jsonify({
                'success': False,
                'error': 'USERNAME_EXISTS',
                'message': '用户名已存在，请选择其他用户名'
            }), 400
        
        if user_repo.get_by_email(email):
            return jsonify({
                'success': False,
                'error': 'EMAIL_EXISTS',
                'message': '邮箱已被注册，请使用其他邮箱'
            }), 400
        
        # 创建用户
        try:
            user = user_repo.create_user(
                username=username,
                email=email,
                password=password,
                nickname=nickname or username
            )
            
            # 生成JWT Token
            jwt_service = JWTService()
            token_result = jwt_service.generate_token(
                user_id=user.id,
                email=user.email,
                is_admin=user.is_admin()
            )
            
            if not token_result['success']:
                return jsonify({
                    'success': False,
                    'error': 'TOKEN_GENERATION_FAILED',
                    'message': 'Token生成失败'
                }), 500
            
            # 设置session
            from flask import session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['username'] = user.username
            session['user_role'] = user.user_role
            session['is_admin'] = user.is_admin()
            session['access_token'] = token_result['data']['access_token']
            
            # 发送欢迎邮件（可选）
            try:
                email_service = EmailService()
                email_service.send_welcome_email(user.email, user.nickname or user.username)
            except Exception as e:
                current_app.logger.warning(f"发送欢迎邮件失败: {e}")
            
            return jsonify({
                'success': True,
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'nickname': user.nickname,
                        'plan_type': user.plan_type,
                        'remaining_quota': user.remaining_quota,
                        'user_role': user.user_role,
                        'email_verified': user.email_verified
                    },
                    'tokens': token_result['data']
                },
                'message': '注册成功！欢迎加入智策股析',
                'timestamp': datetime.utcnow().isoformat()
            }), 201
            
        except Exception as e:
            current_app.logger.error(f"创建用户失败: {e}")
            return jsonify({
                'success': False,
                'error': 'USER_CREATION_FAILED',
                'message': '用户创建失败，请稍后重试'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"用户注册API错误: {e}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500


@auth_api_bp.route('/login', methods=['POST'])
def login():
    """用户登录（用户名密码）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': '请求数据格式错误'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # 验证输入
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'MISSING_CREDENTIALS',
                'message': '用户名和密码为必填项'
            }), 400
        
        # 验证用户
        user_repo = UserRepository(db.session)
        user = user_repo.authenticate_user(username, password)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'INVALID_CREDENTIALS',
                'message': '用户名或密码错误'
            }), 401
        
        # 检查是否为管理员邮箱（特殊处理）
        from app.config import DevelopmentConfig
        config = DevelopmentConfig()
        if user.email == config.ADMIN_EMAIL and user.user_role == 'USER':
            # 如果是管理员邮箱但角色还是普通用户，自动升级为超级管理员
            user_repo.update_user_role(user.id, 'SUPER_ADMIN')
            user.user_role = 'SUPER_ADMIN'
        
        # 检查用户状态
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'USER_DISABLED',
                'message': '用户账户已被禁用'
            }), 403
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 生成JWT Token
        jwt_service = JWTService()
        token_result = jwt_service.generate_token(
            user_id=user.id,
            email=user.email,
            is_admin=user.is_admin()
        )
        
        if not token_result['success']:
            return jsonify({
                'success': False,
                'error': 'TOKEN_GENERATION_FAILED',
                'message': 'Token生成失败'
            }), 500
        
        # 设置session
        from flask import session
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['username'] = user.username
        session['user_role'] = user.user_role
        session['is_admin'] = user.is_admin()
        session['access_token'] = token_result['data']['access_token']
        
        return jsonify({
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'nickname': user.nickname,
                    'plan_type': user.plan_type,
                    'remaining_quota': user.remaining_quota,
                    'user_role': user.user_role,
                    'email_verified': user.email_verified
                },
                'tokens': token_result['data']
            },
            'message': '登录成功',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"用户登录API错误: {e}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500


@auth_api_bp.route('/send-code', methods=['POST'])
def send_verification_code():
    """发送验证码"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': '请求数据格式错误'
            }), 400
        
        email = data.get('email', '').strip().lower()
        
        # 验证邮箱格式
        if not email:
            return jsonify({
                'success': False,
                'error': 'EMAIL_REQUIRED',
                'message': '邮箱地址为必填项'
            }), 400
        
        if not is_valid_email(email):
            return jsonify({
                'success': False,
                'error': 'EMAIL_INVALID',
                'message': '邮箱格式无效'
            }), 400
        
        # 检查是否为管理员邮箱
        from app.config import DevelopmentConfig
        from app.models.user import User
        
        config = DevelopmentConfig()
        if email == config.ADMIN_EMAIL:
            # 管理员邮箱直接登录，无需验证码
            from flask import session
            
            # 从数据库获取实际的用户ID
            admin_user = User.query.filter_by(email=email).first()
            if admin_user:
                session['user_id'] = admin_user.id
                session['user_email'] = email
                session['is_admin'] = True
                session['access_token'] = 'admin_token'
                
                return jsonify({
                    'success': True,
                    'data': {
                        'is_admin': True,
                        'message': '管理员登录成功',
                        'redirect_url': '/dashboard/'
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'ADMIN_NOT_FOUND',
                    'message': '管理员账户不存在，请联系系统管理员'
                }), 400
        
        # 生成验证码
        verification_service = VerificationCodeService()
        result = verification_service.send_code(email)
        
        if not result['success']:
            return jsonify(result), 400
        
        # 发送邮件
        if current_app.config.get('SEND_EMAIL', True):
            email_service = EmailService()
            email_result = email_service.send_verification_code(
                email, 
                result['data']['code']
            )
            
            if not email_result['success']:
                current_app.logger.warning(f"邮件发送失败，但验证码已生成: {email}")
        
        # 返回结果（生产环境不应返回验证码）
        response_data = {
            'message': '验证码已发送到您的邮箱',
            'expires_in': result['data']['expires_in'],
            'email': email
        }
        
        # 开发环境返回验证码便于测试
        if current_app.config.get('DEBUG', False):
            response_data['code'] = result['data']['code']
            response_data['dev_note'] = '开发模式：验证码已返回'
        
        return jsonify({
            'success': True,
            'data': response_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"发送验证码API错误: {e}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500


@auth_api_bp.route('/verify-code', methods=['POST'])
def verify_code():
    """验证登录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': '请求数据格式错误'
            }), 400
        
        email = data.get('email', '').strip().lower()
        code = data.get('code', '').strip()
        
        # 验证输入
        if not email or not code:
            return jsonify({
                'success': False,
                'error': 'MISSING_PARAMETERS',
                'message': '邮箱和验证码为必填项'
            }), 400
        
        if not is_valid_email(email):
            return jsonify({
                'success': False,
                'error': 'EMAIL_INVALID',
                'message': '邮箱格式无效'
            }), 400
        
        if len(code) != 6 or not code.isdigit():
            return jsonify({
                'success': False,
                'error': 'CODE_INVALID',
                'message': '验证码应为6位数字'
            }), 400
        
        # 验证验证码
        verification_service = VerificationCodeService()
        verify_result = verification_service.verify_code(email, code)
        
        if not verify_result['success']:
            return jsonify(verify_result), 400
        
        # 认证或创建用户
        user_service = UserDataService(db.session)
        user = user_service.authenticate_or_create_user(email)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'USER_CREATION_FAILED',
                'message': '用户创建失败'
            }), 500
        
        # 检查用户状态
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'USER_DISABLED',
                'message': '用户账户已被禁用'
            }), 403
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 生成JWT Token
        jwt_service = JWTService()
        token_result = jwt_service.generate_token(
            user_id=user.id,
            email=user.email,
            is_admin=False  # 默认非管理员，管理员通过其他方式登录
        )
        
        if not token_result['success']:
            return jsonify({
                'success': False,
                'error': 'TOKEN_GENERATION_FAILED',
                'message': 'Token生成失败'
            }), 500
        
        # 如果是新用户，发送欢迎邮件
        if user.created_at and (datetime.utcnow() - user.created_at).total_seconds() < 60:
            try:
                email_service = EmailService()
                email_service.send_welcome_email(user.email, user.nickname or '用户')
            except Exception as e:
                current_app.logger.warning(f"发送欢迎邮件失败: {e}")
        
        # 设置session（用于传统页面访问）
        from flask import session
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['is_admin'] = user.is_admin if hasattr(user, 'is_admin') else False
        session['access_token'] = token_result['data']['access_token']
        
        return jsonify({
            'success': True,
            'data': token_result['data'],
            'message': '登录成功',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"验证登录API错误: {e}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500


@auth_api_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """刷新访问Token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': '请求数据格式错误'
            }), 400
        
        refresh_token = data.get('refresh_token', '').strip()
        
        if not refresh_token:
            return jsonify({
                'success': False,
                'error': 'MISSING_REFRESH_TOKEN',
                'message': '刷新Token为必填项'
            }), 400
        
        # 刷新Token
        jwt_service = JWTService()
        result = jwt_service.refresh_token(refresh_token)
        
        if not result['success']:
            return jsonify(result), 401
        
        return jsonify({
            'success': True,
            'data': result['data'],
            'message': 'Token刷新成功',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"刷新Token API错误: {e}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500


@auth_api_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """用户登出"""
    try:
        # 获取当前Token
        auth_header = request.headers.get('Authorization')
        jwt_service = JWTService()
        token = jwt_service.extract_token_from_header(auth_header)
        
        if token:
            # 撤销Token（将来可以实现黑名单）
            jwt_service.revoke_token(token)
        
        return jsonify({
            'success': True,
            'message': '登出成功',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"登出API错误: {e}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500


@auth_api_bp.route('/profile', methods=['GET'])
@jwt_required
def get_profile():
    """获取用户资料"""
    try:
        from flask import g
        
        user_id = g.current_user['user_id']
        
        # 获取用户详细信息
        user_service = UserDataService(db.session)
        profile = user_service.get_user_profile(user_id)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'USER_NOT_FOUND',
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': profile,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取用户资料API错误: {e}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500


@auth_api_bp.route('/profile', methods=['PUT'])
@jwt_required
def update_profile():
    """更新用户资料"""
    try:
        from flask import g
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'INVALID_REQUEST',
                'message': '请求数据格式错误'
            }), 400
        
        user_id = g.current_user['user_id']
        nickname = data.get('nickname', '').strip()
        
        # 验证昵称
        if nickname and (len(nickname) > 50 or len(nickname) < 1):
            return jsonify({
                'success': False,
                'error': 'INVALID_NICKNAME',
                'message': '昵称长度应在1-50字符之间'
            }), 400
        
        # 更新用户资料
        user_service = UserDataService(db.session)
        result = user_service.update_user_profile(user_id, nickname=nickname)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify({
            'success': True,
            'data': result['data'],
            'message': '用户资料更新成功',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"更新用户资料API错误: {e}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500


@auth_api_bp.route('/status', methods=['GET'])
@jwt_required
def status():
    """检查登录状态"""
    try:
        from flask import g
        
        return jsonify({
            'success': True,
            'data': {
                'authenticated': True,
                'user': g.current_user
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"检查登录状态API错误: {e}")
        return jsonify({
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }), 500